#!/usr/bin/env python3
"""
Konwerter Turbo 2000F+ NEW FORMAT.

Narzędzie pracuje w dwóch kierunkach:
  * decode: z tekstowego .hex wycina bloki PWMD i składa z nich XEX,
  * encode: z DOS binary/XEX buduje strumień PWMD zapisywany jako .hex albo .cas.

W praktycznych nagraniach new-format pierwszy blok nazwy i opcjonalny loader
nadal używają starego/standardowego formatu Turbo 2000. Dopiero właściwe bloki
programu mają układ NEW FORMAT: osobny nagłówek zakresu adresów, osobny blok
danych oraz końcowy bajt 00 po sumie kontrolnej.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

BYTE_RE = re.compile(r"^(?:\$|0x)?([0-9a-fA-F]{1,2})$")

STD_BLOCK_DATA_SIZE = 3072
DEFAULT_BIT0_PULSE = 12
DEFAULT_BIT1_PULSE = 24
DEFAULT_PWM_SAMPLE_RATE = 48000
DEFAULT_PWM_PILOT_PULSE = 48


@dataclass(frozen=True)
class PwmdBlock:
    """Jeden fizyczny blok danych PWMD odczytany z pliku .hex."""

    index: int          # 1-based pwmd block number in file
    line_no: int
    data: bytes        # bytes after: pwmd <zero> <one> ...


@dataclass(frozen=True)
class Segment:
    """Jeden segment DOS binary/XEX: zakres adresów Atari plus dane."""

    start: int
    end: int
    data: bytes


class T2KFError(Exception):
    pass


class DecodeError(T2KFError):
    pass


class EncodeError(T2KFError):
    pass


def parse_byte_token(tok: str) -> int:
    m = BYTE_RE.match(tok)
    if not m:
        raise ValueError(tok)
    return int(m.group(1), 16)


def checksum_mod256(data: bytes) -> int:
    return sum(data) & 0xFF


def u16le(data: bytes, offset: int = 0) -> int:
    return data[offset] | (data[offset + 1] << 8)


def put_u16le(value: int) -> bytes:
    if not 0 <= value <= 0xFFFF:
        raise ValueError(value)
    return bytes((value & 0xFF, value >> 8))


def hex_bytes(data: bytes) -> str:
    return " ".join(f"{b:02x}" for b in data)


# ---------------------------------------------------------------------------
# DECODER
# ---------------------------------------------------------------------------

def parse_pwmd_blocks(path: Path) -> list[PwmdBlock]:
    """
    Wyciąga tylko linie PWMD z tekstowego pliku .hex.

    Linie sterujące typu FUJI/pwms/pwmc są ważne dla nagrania taśmy, ale nie
    niosą bajtów programu, więc dekoder danych może je bezpiecznie pominąć.
    """
    blocks: list[PwmdBlock] = []

    for line_no, raw_line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        line = raw_line.split(";", 1)[0].strip()
        if not line:
            continue

        parts = line.split()
        if not parts or parts[0].lower() != "pwmd":
            continue

        if len(parts) < 4:
            raise DecodeError(f"linia {line_no}: za krótka linia pwmd")

        # hex:
        #   pwmd <bit0-pulse> <bit1-pulse> <bytes...>
        data = bytearray()
        for tok in parts[3:]:
            try:
                data.append(parse_byte_token(tok))
            except ValueError:
                raise DecodeError(
                    f"linia {line_no}: niepoprawny bajt hex: {tok!r}"
                ) from None

        blocks.append(PwmdBlock(index=len(blocks) + 1, line_no=line_no, data=bytes(data)))

    return blocks


def verify_old_turbo_block(block: PwmdBlock, what: str) -> bytes:
    """
    Oryginalny/standardowy blok Turbo 2000:
        payload... checksum

    Blok nazwy i blok loadera w Turbo 2000F+ new format są jeszcze w tym
    starym formacie, czyli NIE mają końcowego bajtu 00 po sumie kontrolnej.
    """
    if len(block.data) < 2:
        raise DecodeError(f"{what}: linia {block.line_no}: blok za krótki")

    payload = block.data[:-1]
    got = block.data[-1]
    expected = checksum_mod256(payload)

    if got != expected:
        raise DecodeError(
            f"{what}: linia {block.line_no}: zła suma: "
            f"jest ${got:02X}, powinno być ${expected:02X}"
        )

    return payload


def verify_new_turbo_block(block: PwmdBlock, what: str) -> bytes:
    """
    Blok właściwy Turbo 2000F+ new format:
        payload... checksum 00
    """
    if len(block.data) < 2:
        raise DecodeError(f"{what}: linia {block.line_no}: blok za krótki")

    payload = block.data[:-2]
    got = block.data[-2]
    trailing = block.data[-1]

    if trailing != 0x00:
        raise DecodeError(
            f"{what}: linia {block.line_no}: ostatni bajt nie jest zerem: "
            f"${trailing:02X}"
        )

    expected = checksum_mod256(payload)

    if got != expected:
        raise DecodeError(
            f"{what}: linia {block.line_no}: zła suma: "
            f"jest ${got:02X}, powinno być ${expected:02X}"
        )

    return payload


def decode_standard_name_block(block: PwmdBlock) -> str:
    """
    Standardowy blok nazwy Turbo 2000:
        00 FF <10 znaków nazwy> checksum
    """
    payload = verify_old_turbo_block(block, "blok nazwy")

    if len(payload) != 12:
        raise DecodeError(
            f"blok nazwy: linia {block.line_no}: payload powinien mieć "
            f"12 bajtów: 00 FF + 10 znaków, ma {len(payload)}"
        )

    if payload[0:2] != b"\x00\xff":
        raise DecodeError(
            f"blok nazwy: linia {block.line_no}: brak znacznika 00 FF"
        )

    return payload[2:12].decode("latin-1", errors="replace").rstrip(" ")


def decode_standard_data_block(block: PwmdBlock, what: str) -> tuple[int, bytes]:
    """
    Standardowy blok danych Turbo 2000:
        length_lo length_hi 3072 bajty danych/padding checksum

    Zwraca: (length, data_without_padding).
    """
    payload = verify_old_turbo_block(block, what)

    if len(payload) != 2 + STD_BLOCK_DATA_SIZE:
        raise DecodeError(
            f"{what}: linia {block.line_no}: payload powinien mieć "
            f"{2 + STD_BLOCK_DATA_SIZE} bajty: length + 3072 danych/paddingu, "
            f"ma {len(payload)}"
        )

    data_len = u16le(payload, 0)
    if data_len > STD_BLOCK_DATA_SIZE:
        raise DecodeError(
            f"{what}: linia {block.line_no}: błędna długość danych "
            f"{data_len}, większa niż {STD_BLOCK_DATA_SIZE}"
        )

    return data_len, payload[2:2 + data_len]


def extract_loader_xex(blocks: list[PwmdBlock]) -> bytes:
    """
    Zwraca opcjonalny loader zapisany na początku taśmy w starym formacie.

    Układ obsługiwany przez tę funkcję to:
      1. standardowy blok nazwy Turbo 2000,
      2. standardowy blok danych zawierający loader XEX.
    """
    if len(blocks) < 2:
        raise DecodeError("brak bloku loadera: plik ma mniej niż dwa bloki pwmd")

    # Zweryfikuj blok nazwy przy okazji, żeby wcześnie złapać przesunięcie.
    decode_standard_name_block(blocks[0])
    _loader_len, loader_xex = decode_standard_data_block(blocks[1], "blok loadera")

    if len(loader_xex) < 2 or loader_xex[:2] != b"\xff\xff":
        raise DecodeError("blok loadera: wycięty loader nie zaczyna się od FF FF")

    return loader_xex


def decode_new_format_blocks(blocks: list[PwmdBlock], *, verbose: bool = False) -> list[Segment]:
    """
    Dekoduje właściwą część Turbo 2000F+ NEW FORMAT do segmentów XEX.

    Strumień składa się z par bloków PWMD:
      header: start/end albo FF FF start/end dla pierwszego segmentu,
      data:   bajty segmentu o długości wynikającej z zakresu adresów.

    Koniec pliku jest oznaczony specjalnym nagłówkiem FF FF FF FF.
    """
    segments: list[Segment] = []
    i = 0
    first_header = True

    while i < len(blocks):
        hb = blocks[i]
        header = verify_new_turbo_block(hb, "nagłówek")

        # EOF:
        #   FF FF FF FF FC 00
        # payload:
        #   FF FF FF FF
        if header == b"\xff\xff\xff\xff":
            if verbose:
                print(f"EOF: pwmd#{hb.index}, line={hb.line_no}", file=sys.stderr)
            return segments

        if first_header:
            # Pierwszy nagłówek ma prefiks FF FF, analogiczny do znacznika
            # DOS binary/XEX. Kolejne nagłówki przechowują już tylko start/end.
            if len(header) != 6:
                raise DecodeError(
                    f"linia {hb.line_no}: pierwszy nagłówek powinien mieć "
                    f"6 bajtów payloadu: FF FF start end, ma {len(header)}"
                )
            if header[0:2] != b"\xff\xff":
                raise DecodeError(
                    f"linia {hb.line_no}: pierwszy nagłówek nie zaczyna się od FF FF"
                )

            start_addr = u16le(header, 2)
            end_addr = u16le(header, 4)
            first_header = False
        else:
            if len(header) != 4:
                raise DecodeError(
                    f"linia {hb.line_no}: nagłówek powinien mieć "
                    f"4 bajty payloadu: start end, ma {len(header)}"
                )

            start_addr = u16le(header, 0)
            end_addr = u16le(header, 2)

        if end_addr < start_addr:
            raise DecodeError(
                f"linia {hb.line_no}: błędny zakres "
                f"${start_addr:04X}-${end_addr:04X}"
            )

        if i + 1 >= len(blocks):
            raise DecodeError(
                f"linia {hb.line_no}: nagłówek "
                f"${start_addr:04X}-${end_addr:04X} nie ma bloku danych"
            )

        db = blocks[i + 1]
        data = verify_new_turbo_block(db, f"dane ${start_addr:04X}-${end_addr:04X}")

        # Długość bloku danych nie jest zapisana osobnym polem. Wynika wprost
        # z inkluzywnego zakresu adresów Atari: end - start + 1.
        expected_len = end_addr - start_addr + 1
        if len(data) != expected_len:
            raise DecodeError(
                f"linia {db.line_no}: zła długość danych dla "
                f"${start_addr:04X}-${end_addr:04X}: "
                f"jest {len(data)}, powinno być {expected_len}"
            )

        segments.append(Segment(start=start_addr, end=end_addr, data=data))

        if verbose:
            print_segment("segment", len(segments), hb.index, db.index, hb.line_no, db.line_no, start_addr, end_addr, len(data))

        i += 2

    raise DecodeError("brak końcowego bloku EOF: FF FF FF FF FC 00")


def print_segment(prefix: str, n: int, hb_index: int | None, db_index: int | None,
                  hb_line: int | None, db_line: int | None,
                  start_addr: int, end_addr: int, data_len: int) -> None:
    """Wspólny, diagnostyczny wydruk segmentów dla trybu verbose."""
    seg = Segment(start_addr, end_addr, b"" * data_len)
    tags: list[str] = []
    if segment_contains_runad(seg):
        tags.append("RUNAD")
    if segment_contains_initad(seg):
        tags.append("INITAD")
    tag = " " + "+".join(tags) if tags else ""

    if hb_index is None:
        print(
            f"{prefix} {n:3d}: ${start_addr:04X}-${end_addr:04X} "
            f"{data_len:6d} bytes{tag}",
            file=sys.stderr,
        )
    else:
        print(
            f"{prefix} {n:3d}: "
            f"pwmd#{hb_index:3d}/#{db_index:3d} "
            f"line {hb_line:5d}/{db_line:5d} "
            f"${start_addr:04X}-${end_addr:04X} "
            f"{data_len:6d} bytes{tag}",
            file=sys.stderr,
        )




def segment_contains_range(seg: Segment, start: int, end: int) -> bool:
    return seg.start <= start and seg.end >= end


def segment_contains_initad(seg: Segment) -> bool:
    # INITAD is the two-byte vector at $02E2-$02E3.
    # A segment may be exactly $02E2-$02E3, but it may also be a combined
    # RUNAD+INITAD vector segment like $02E0-$02E3. Both cases require
    # the longer pilot/sync before the next header in Turbo 2000F+ new format.
    return segment_contains_range(seg, 0x02E2, 0x02E3)


def segment_contains_runad(seg: Segment) -> bool:
    # RUNAD is the two-byte vector at $02E0-$02E1.
    return segment_contains_range(seg, 0x02E0, 0x02E1)

def write_xex(path: Path, segments: list[Segment]) -> None:
    """Zapisuje segmenty jako klasyczny Atari DOS binary/XEX."""
    out = bytearray(b"\xff\xff")

    for seg in segments:
        out += put_u16le(seg.start)
        out += put_u16le(seg.end)
        out += seg.data

    path.write_bytes(out)


# ---------------------------------------------------------------------------
# ENCODER
# ---------------------------------------------------------------------------

def read_xex_segments(path: Path) -> list[Segment]:
    """
    Czyta Atari DOS binary/XEX do listy segmentów.

    Format XEX składa się z globalnego FF FF, po którym występują rekordy
    start/end/data. Znacznik FF FF może też pojawić się ponownie między
    segmentami, dlatego parser toleruje go w każdym miejscu początku rekordu.
    """
    data = path.read_bytes()
    pos = 0
    segments: list[Segment] = []

    if len(data) < 2:
        raise EncodeError("XEX za krótki: brak nagłówka FF FF")

    while pos < len(data):
        # DOS binary may contain FF FF marker before first segment and also between segments.
        if pos + 2 <= len(data) and data[pos:pos + 2] == b"\xff\xff":
            pos += 2
            if pos == len(data):
                break

        if pos + 4 > len(data):
            raise EncodeError(f"XEX ucięty przy pozycji {pos}: brak start/end")

        start = u16le(data, pos)
        end = u16le(data, pos + 2)
        pos += 4

        if end < start:
            raise EncodeError(f"XEX: błędny zakres ${start:04X}-${end:04X}")

        length = end - start + 1
        if pos + length > len(data):
            raise EncodeError(
                f"XEX ucięty w segmencie ${start:04X}-${end:04X}: "
                f"potrzeba {length} bajtów, zostało {len(data) - pos}"
            )

        seg_data = data[pos:pos + length]
        pos += length
        segments.append(Segment(start=start, end=end, data=seg_data))

    if not segments:
        raise EncodeError("XEX nie zawiera żadnych segmentów")

    return segments


def make_new_block(payload: bytes) -> bytes:
    # NEW FORMAT: payload + suma modulo 256 + końcowe 00.
    return payload + bytes((checksum_mod256(payload), 0x00))


def make_old_block(payload: bytes) -> bytes:
    # Standardowy Turbo 2000: payload + sama suma modulo 256.
    return payload + bytes((checksum_mod256(payload),))


def make_standard_name_block(name: str) -> bytes:
    # Format standardowy: 00 FF + 10 bajtów nazwy dopełnionej spacjami + checksum.
    raw = name.encode("latin-1", errors="replace")[:10]
    raw = raw.ljust(10, b" ")
    return make_old_block(b"\x00\xff" + raw)


def make_standard_loader_block(loader_xex: bytes) -> bytes:
    if len(loader_xex) > STD_BLOCK_DATA_SIZE:
        raise EncodeError(
            f"loader ma {len(loader_xex)} bajtów, a standardowy blok Turbo 2000 "
            f"mieści maksymalnie {STD_BLOCK_DATA_SIZE} bajty"
        )
    if len(loader_xex) < 2 or loader_xex[:2] != b"\xff\xff":
        raise EncodeError("loader podany przez --add-loader nie zaczyna się od FF FF")

    payload = bytearray()
    payload += put_u16le(len(loader_xex))
    payload += loader_xex
    payload += b"\x00" * (STD_BLOCK_DATA_SIZE - len(loader_xex))
    return make_old_block(bytes(payload))


def default_tape_name_from_path(path: Path) -> str:
    # Bezpieczna, przewidywalna nazwa do starego bloku nazwy: uppercase, max 10.
    s = path.stem.upper()
    # Stary blok nazwy ma 10 bajtów. Zostawiamy tylko dość bezpieczne znaki.
    s = "".join(ch if 32 <= ord(ch) <= 126 else "_" for ch in s)
    return s[:10] or "NONAME"


class HexWriter:
    """Writer generujący tekstowy .hex z liniami pwmc/pwmd."""

    def __init__(self, fp, *, bit0: int = DEFAULT_BIT0_PULSE, bit1: int = DEFAULT_BIT1_PULSE):
        self.fp = fp
        self.bit0 = bit0
        self.bit1 = bit1
        self.block_no = 0

    def header(self, title: str) -> None:
        self.fp.write("A8CAS-HEX\n")
        self.fp.write(f"FUJI {title}\n")
        self.fp.write(f"pwms msb_first rising_edge_first {DEFAULT_PWM_SAMPLE_RATE}\n")

    def pwmc(self, *args: int, count: int = 1) -> None:
        # Zapisujemy dokładnie w stylu plików z a8cas-util.pl.
        arg_s = " ".join(str(a) for a in args)
        self.fp.write(f"pwmc 00000 {arg_s} ; count={count}\n")

    def pwmd(self, data: bytes) -> None:
        self.block_no += 1
        # W blokach NEW FORMAT suma jest przed końcowym 00, w starych blokach
        # jest ostatnim bajtem. Komentarz w .hex pokazuje właściwą wartość.
        chk = data[-2] if len(data) >= 2 and data[-1] == 0 else data[-1]
        self.fp.write(
            f"pwmd {self.bit0} {self.bit1} {hex_bytes(data)} "
            f"; block no={self.block_no} ; length={len(data)} "
            f"; checksum(modulo256)={chk:02x} OK\n"
        )


class CasWriter:
    """
    Binary CAS writer for PWM chunks.

    CAS chunk layout:
        4 bytes chunk type
        2 bytes chunk length, not including the 8-byte header
        2 bytes aux, meaning depends on chunk type
        chunk_length bytes data
    """

    PWMS_RISING_EDGE_FIRST = 0b10
    PWMS_MSB_FIRST = 0b100

    def __init__(self, fp, *, bit0: int = DEFAULT_BIT0_PULSE, bit1: int = DEFAULT_BIT1_PULSE):
        self.fp = fp
        self.bit0 = bit0
        self.bit1 = bit1
        self.block_no = 0

    def chunk(self, chunk_type: bytes, aux: int, data: bytes = b"") -> None:
        if len(chunk_type) != 4:
            raise EncodeError(f"CAS: chunk type musi mieć 4 bajty, jest {chunk_type!r}")
        if len(data) > 0xFFFF:
            raise EncodeError(
                f"CAS: chunk {chunk_type.decode('ascii', errors='replace')} "
                f"ma {len(data)} bajtów, maksimum dla CAS to 65535"
            )
        self.fp.write(chunk_type)
        self.fp.write(put_u16le(len(data)))
        self.fp.write(put_u16le(aux))
        self.fp.write(data)

    def header(self, title: str) -> None:
        # FUJI must be the first CAS chunk. Description is UTF-8.
        self.chunk(b"FUJI", 0, title.encode("utf-8"))

        # pwms: aux byte 0 = flags, aux byte 1 ignored/reserved.
        #   pulse_type %10 = rising edge first
        #   bit_order bit2 = MSB first
        flags = self.PWMS_RISING_EDGE_FIRST | self.PWMS_MSB_FIRST
        self.chunk(b"pwms", flags, put_u16le(DEFAULT_PWM_SAMPLE_RATE))

    def pwmc(self, *args: int, count: int = 1) -> None:
        # HexWriter receives: pulse,count[, pulse,count...].
        if len(args) % 2 != 0:
            raise EncodeError("CAS pwmc: oczekiwano par pulse,count")
        data = bytearray()
        for pulse, pulses_count in zip(args[0::2], args[1::2]):
            if not 0 <= pulse <= 0xFF:
                raise EncodeError(f"CAS pwmc: długość pulsu poza zakresem bajtu: {pulse}")
            if not 0 <= pulses_count <= 0xFFFF:
                raise EncodeError(f"CAS pwmc: liczba pulsów poza zakresem word: {pulses_count}")
            data.append(pulse)
            data += put_u16le(pulses_count)
        self.chunk(b"pwmc", 0, bytes(data))

    def pwmd(self, data: bytes) -> None:
        self.block_no += 1
        aux = self.bit0 | (self.bit1 << 8)
        self.chunk(b"pwmd", aux, data)


def output_format_from_args(output_path: Path, requested: str) -> str:
    """Rozstrzyga format zapisu przy --encode."""
    if requested != "auto":
        return requested
    suffix = output_path.suffix.lower()
    if suffix == ".cas":
        return "cas"
    return "hex"


def open_output_writer(output_path: Path, output_format: str):
    """Otwiera plik wyjściowy i dobiera writer zgodny z wybranym formatem."""
    if output_format == "hex":
        fp = output_path.open("w", encoding="ascii", newline="\n")
        return fp, HexWriter(fp)
    if output_format == "cas":
        fp = output_path.open("wb")
        return fp, CasWriter(fp)
    raise EncodeError(f"nieznany format wyjściowy: {output_format}")


def write_encoded_file(
    output_path: Path,
    segments: list[Segment],
    *,
    output_format: str,
    title: str,
    tape_name: str | None,
    loader_path: Path | None,
    verbose: bool = False,
) -> None:
    """
    Koduje segmenty XEX jako strumień Turbo 2000F+ NEW FORMAT.

    Opcjonalnie poprzedza właściwy new-format standardowym blokiem nazwy i
    blokiem loadera, żeby uzyskać taśmę podobną do oryginalnych nagrań.
    """
    fp, w = open_output_writer(output_path, output_format)
    with fp:
        w.header(title)

        if loader_path is not None:
            # Loader jest zwykłym blokiem danych Turbo 2000, więc musi zmieścić
            # się w pojedynczym standardowym rekordzie 3072 bajtów.
            name = tape_name if tape_name is not None else default_tape_name_from_path(output_path)
            loader_xex = loader_path.read_bytes()

            name_block = make_standard_name_block(name)
            loader_block = make_standard_loader_block(loader_xex)

            # Standard Turbo 2000: blok nazwy i loader. W Twoich znormalizowanych
            # plikach było tu pwmc ... 3072; trzymamy się tego układu.
            w.pwmc(DEFAULT_PWM_PILOT_PULSE, 3072)
            w.pwmd(name_block)
            w.pwmc(DEFAULT_PWM_PILOT_PULSE, 3072)
            w.pwmd(loader_block)

            if verbose:
                print(
                    f"added loader: {loader_path} ({len(loader_xex)} bytes), "
                    f"name={name!r}",
                    file=sys.stderr,
                )

        # Pierwszy blok właściwego new-format ma dłuższy pilot i nagłówek FF FF start end.
        first = True
        for idx, seg in enumerate(segments, 1):
            if first:
                w.pwmc(DEFAULT_PWM_PILOT_PULSE, 1, DEFAULT_PWM_PILOT_PULSE, 3072, count=2)
                header_payload = b"\xff\xff" + put_u16le(seg.start) + put_u16le(seg.end)
                first = False
            else:
                # Po INITAD standard przewiduje 768 impulsów; w .hex wystarczy to
                # jawnie opisać jako pilot przed następnym nagłówkiem.
                prev = segments[idx - 2]
                if segment_contains_initad(prev):
                    w.pwmc(DEFAULT_PWM_PILOT_PULSE, 768)
                else:
                    w.pwmc(DEFAULT_PWM_PILOT_PULSE, 6)
                header_payload = put_u16le(seg.start) + put_u16le(seg.end)

            w.pwmd(make_new_block(header_payload))
            # Po nagłówku idzie krótki pilot i blok danych tego samego segmentu.
            w.pwmc(DEFAULT_PWM_PILOT_PULSE, 11)
            w.pwmd(make_new_block(seg.data))

            if verbose:
                print_segment("encoded", idx, None, None, None, None, seg.start, seg.end, len(seg.data))

        # EOF: payload FF FF FF FF, checksum FC, trailing 00.
        w.pwmc(DEFAULT_PWM_PILOT_PULSE, 6)
        w.pwmd(make_new_block(b"\xff\xff\xff\xff"))


def encode_command(args: argparse.Namespace) -> int:
    """Obsługa trybu XEX -> HEX/CAS."""
    segments = read_xex_segments(args.input)
    output_format = output_format_from_args(args.output, args.format)
    write_encoded_file(
        args.output,
        segments,
        output_format=output_format,
        title=args.title if args.title is not None else args.input.stem,
        tape_name=args.tape_name,
        loader_path=args.add_loader,
        verbose=args.verbose,
    )

    if args.verbose:
        print(
            f"written: {args.output} format={output_format} segments={len(segments)} "
            f"data_bytes={sum(len(s.data) for s in segments)}",
            file=sys.stderr,
        )
    return 0


def decode_command(args: argparse.Namespace) -> int:
    """Obsługa trybu HEX -> XEX."""
    blocks = parse_pwmd_blocks(args.input)

    if args.verbose:
        print(f"pwmd blocks: {len(blocks)}", file=sys.stderr)

    if args.extract_loader is not None:
        loader_xex = extract_loader_xex(blocks)
        args.extract_loader.write_bytes(loader_xex)

        if args.verbose:
            print(
                f"loader written: {args.extract_loader} "
                f"({len(loader_xex)} bytes)",
                file=sys.stderr,
            )

    if args.skip_loader:
        # Po odrzuceniu dwóch starych bloków reszta strumienia powinna zaczynać
        # się już od pierwszego nagłówka NEW FORMAT.
        if len(blocks) < 3:
            raise DecodeError("--skip-loader: plik ma mniej niż trzy bloki pwmd")

        if args.verbose:
            tape_name = decode_standard_name_block(blocks[0])
            loader_len, _loader_xex = decode_standard_data_block(blocks[1], "blok loadera")
            print(
                f"skipped name:   pwmd#{blocks[0].index}, line={blocks[0].line_no}, "
                f"name={tape_name!r}",
                file=sys.stderr,
            )
            print(
                f"skipped loader: pwmd#{blocks[1].index}, line={blocks[1].line_no}, "
                f"data_len={loader_len} bytes, physical_data={STD_BLOCK_DATA_SIZE} bytes",
                file=sys.stderr,
            )

        blocks = blocks[2:]

    segments = decode_new_format_blocks(blocks, verbose=args.verbose)
    write_xex(args.output, segments)

    if args.verbose:
        print(
            f"written: {args.output} "
            f"segments={len(segments)} "
            f"data_bytes={sum(len(s.data) for s in segments)}",
            file=sys.stderr,
        )
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Decode/encode Turbo 2000F+ new format .hex/.cas and Atari DOS binary/XEX."
    )
    ap.add_argument("input", type=Path, help="wejściowy .hex dla dekodowania albo .xex dla --encode")
    ap.add_argument("output", type=Path, help="wyjściowy .xex dla dekodowania albo .hex/.cas dla --encode")

    ap.add_argument(
        "--encode",
        action="store_true",
        help="koduj XEX/DOS binary do .hex/.cas Turbo 2000F+ new format",
    )
    ap.add_argument(
        "--format",
        choices=("auto", "hex", "cas"),
        default="auto",
        help="encode: format wyjściowy; auto wybiera cas dla .cas, inaczej hex",
    )

    # Decode options.
    ap.add_argument(
        "--skip-loader",
        action="store_true",
        help="decode: pomiń pierwszy blok pwmd z nazwą i drugi blok pwmd z loaderem",
    )
    ap.add_argument(
        "--extract-loader",
        type=Path,
        metavar="LOADER.XEX",
        help="decode: wyciągnij loader z drugiego bloku pwmd i zapisz jako DOS binary/XEX",
    )

    # Encode options.
    ap.add_argument(
        "--add-loader",
        type=Path,
        metavar="LOADER.XEX",
        help="encode: dodaj standardowy blok nazwy i jeden standardowy blok loadera Turbo 2000",
    )
    ap.add_argument(
        "--tape-name",
        metavar="NAME",
        help="encode: nazwa do standardowego bloku nazwy, max 10 bajtów; domyślnie stem pliku output",
    )
    ap.add_argument(
        "--title",
        metavar="TEXT",
        help="encode: opisowa linia FUJI w .hex; domyślnie stem pliku wejściowego",
    )

    ap.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="wypisz szczegóły operacji",
    )
    return ap


def main() -> int:
    ap = build_arg_parser()
    args = ap.parse_args()

    try:
        if args.encode:
            if args.skip_loader or args.extract_loader is not None:
                raise EncodeError("--skip-loader/--extract-loader mają sens tylko przy dekodowaniu")
            return encode_command(args)

        if args.add_loader is not None or args.tape_name is not None or args.title is not None or args.format != "auto":
            raise DecodeError("--add-loader/--tape-name/--title/--format mają sens tylko z --encode")
        return decode_command(args)

    except T2KFError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

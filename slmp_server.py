# version: iq-r-iq-f-20260624
# =============================================================================
# 簡易 SLMP サーバ 使い方
# =============================================================================
#
# ■ 概要
#   三菱PLCの SLMP 3Eフレーム / バイナリ通信を簡易的にまねる
#   テスト用サーバです。iQ-R形式とiQ-Fで使われるQ/L互換形式の
#   デバイス指定を自動判別します。
#
#   クライアントから「デバイス一括読み出し（0401）」要求が来ると、
#   D/M/X/Y などの指定デバイスに対して、ダミー値を返します。
#
#   また、「デバイス一括書き込み（1401）」要求が来た場合は、
#   データ内容を内部メモリへ反映せず、受け入れたことにして正常応答を
#   返します。
#
#   ただし、PLCそのものを完全に再現するものではありません。
#   読み出し値を内部メモリとして保持しているわけではなく、要求が来るたびに
#   あらかじめ選んだルールで値を作って返します。
#
# -----------------------------------------------------------------------------
# ■ 起動方法
# -----------------------------------------------------------------------------
#
#   python slmp_server_bit_tcp.py
#
#   これで、下記の条件で待ち受けます。
#
#     通信方式 : TCP
#     IP       : 0.0.0.0
#                ※すべてのネットワークインターフェースで待ち受けます。
#     ポート   : 1025
#     フレーム : 3E
#     コード   : バイナリ
#
#   起動すると、socket / hostname / ipconfig から取得した
#   ローカルIPアドレス候補も表示します。
#
#     例：
#       listening on TCP bind=0.0.0.0 port=1025
#       connect address candidates from this PC:
#         192.168.1.50:1025
#         same PC only: 127.0.0.1:1025
#
#   注意：
#     0.0.0.0 は「全てのNICで待ち受ける」という意味です。
#     クライアント側の接続先には、表示された 192.168.x.x などの
#     ローカルIPアドレスを指定してください。
#
# -----------------------------------------------------------------------------
# ■ 他のPCやPLCクライアントから接続したい場合
# -----------------------------------------------------------------------------
#
#   python slmp_server_bit_tcp.py -s 0.0.0.0 -p 5000
#
#   -s 0.0.0.0 とすると、そのPCの全ネットワークインターフェースで
#   待ち受けます。
#
#   例：サーバPCのIPアドレスが 192.168.1.50 の場合、
#       クライアント側は 192.168.1.50:5000 に接続します。
#
# -----------------------------------------------------------------------------
# ■ ポート番号を変えたい場合
# -----------------------------------------------------------------------------
#
#   python slmp_server_bit_tcp.py -p 5000
#
#   -p または --port でポート番号を指定します。
#   省略時は 10000 です。
#
# -----------------------------------------------------------------------------
# ■ UDPで使いたい場合
# -----------------------------------------------------------------------------
#
#   python slmp_server_bit_tcp.py -u
#
#   通常はTCPで動きます。
#   UDPで待ち受けたい場合だけ -u または --udp を付けます。
#
# -----------------------------------------------------------------------------
# ■ 対応している要求
# -----------------------------------------------------------------------------
#
#   対応しているのは、基本的に下記だけです。
#
#     コマンド : 0401  デバイス一括読み出し
#                1401  デバイス一括書き込み
#     形式     : 3E バイナリ
#                iQ-F/Q/L互換サブコマンド  0000/0001
#                iQ-Rサブコマンド          0002/0003
#
#   書き込みについて：
#     受信した書き込みデータはログ表示だけして、内部メモリには反映しません。
#     クライアント側の「書き込み通信が成功するか」の確認用です。
#
#   未対応：
#     ・書き込み値の保持
#     ・ランダム読み出し
#     ・モニタ登録
#     ・4Eフレームの本実装
#     ・ASCIIフレームの本実装
#     ・実PLCのようなメモリ保持
#
# -----------------------------------------------------------------------------
# ■ 対応デバイス
# -----------------------------------------------------------------------------
#
#   ビットデバイス：
#     SM, X, Y, M, L, F, V, B, TS, TC, SS, SC,
#     CS, CC, SB, S, DX, DY
#
#   ワードデバイス：
#     SD, D, W, TN, SN, CN, SW, Z, R, ZR
#
#   例：
#     M100 を 10点読む
#     X0   を 16点読む
#     Y20  を 8点読む
#     D100 を 10ワード読む
#
# -----------------------------------------------------------------------------
# ■ ビットデバイスの返し方を変える
# -----------------------------------------------------------------------------
#
#   -B または --bit-func で、X/Y/Mなどのビット値の作り方を変えられます。
#
#     c0    : 全部OFFを返す
#     c1    : 全部ONを返す
#     alt   : 0,1,0,1... を返す  ※デフォルト
#     alt2  : 0,0,1,1,0,0,1,1... を返す
#     rand  : ランダムにON/OFFを返す
#
#   例：MやXやYを全部ONに見せたい場合
#
#     python slmp_server_bit_tcp.py -B c1
#
#   例：ランダムにON/OFFさせたい場合
#
#     python slmp_server_bit_tcp.py -B rand
#
# -----------------------------------------------------------------------------
# ■ ワードデバイスの返し方を変える
# -----------------------------------------------------------------------------
#
#   -F または --func で、D/W/Rなどのワード値の作り方を変えられます。
#
#     c1    : 全部 1 を返す
#     r10   : 0〜9 くらいの値を時刻ベースで返す
#     r100  : 0〜99 くらいの値を時刻ベースで返す  ※デフォルト
#     rand  : 0〜99 のランダム値を返す
#     inc   : 要求ごとにカウントアップする値を返す
#
#   例：Dレジスタを全部1に見せたい場合
#
#     python slmp_server_bit_tcp.py -F c1
#
#   例：Dレジスタをカウントアップさせたい場合
#
#     python slmp_server_bit_tcp.py -F inc
#
# -----------------------------------------------------------------------------
# ■ よく使いそうな起動例
# -----------------------------------------------------------------------------
#
#   1) 同じPC上でテストする
#
#      python slmp_server_bit_tcp.py
#
#   2) LAN内の別PCから接続する。TCP、ポート5000で待ち受け
#
#      python slmp_server_bit_tcp.py -s 0.0.0.0 -p 5000
#
#   3) M/X/Yなどのビットを全部ONにする
#
#      python slmp_server_bit_tcp.py -B c1
#
#   4) D/W/Rなどのワードをカウントアップさせる
#
#      python slmp_server_bit_tcp.py -F inc
#
#   5) UDPで待ち受ける
#
#      python slmp_server_bit_tcp.py -u -s 0.0.0.0 -p 5000
#
# -----------------------------------------------------------------------------
# ■ 注意
# -----------------------------------------------------------------------------
#
#   ・Windowsでポートを開けない場合は、ファイアウォール設定を確認してください。
#   ・1024以下のポートは環境によって管理者権限が必要です。
#   ・このサーバは値を保持しません。
#       例：M100に書き込んでも、その値をM100から読むことはできません。
#       書き込み要求には正常応答を返しますが、データは破棄します。
#   ・X/Y/Mなどのビット単位読み出しでは、SLMPバイナリの仕様に合わせて
#     1バイトに2点分のビット値を詰めて返します。
#
# =============================================================================

from socketserver import UDPServer, TCPServer
from socketserver import DatagramRequestHandler, StreamRequestHandler
import argparse
import random
import re
import socket
import subprocess
import struct
import time


# -----------------------------------------------------------------------------
# 簡易 SLMP サーバ
#   - 3E フレーム / バイナリコード想定
#   - TCP をデフォルトに変更
#   - D/W/R などのワードデバイス読み出し
#   - X/Y/M などのビットデバイス読み出しに対応
#   - 一括書き込み(1401)は受信だけして正常応答を返す
# -----------------------------------------------------------------------------


CMD_DEVICE_READ = 0x0401
CMD_DEVICE_WRITE = 0x1401
SUBCMD_WORD_UNITS = 0x0000
SUBCMD_BIT_UNITS = 0x0001
SUBCMD_IQR_WORD_UNITS = 0x0002
SUBCMD_IQR_BIT_UNITS = 0x0003

# よく使うデバイスコード。
# ※ここでは簡易サーバなので、実メモリは持たず、要求アドレスに応じた保持値も持ちません。
BIT_DEVICES = {
    0x91: "SM", # special relay
    0x9C: "X",  # input relay
    0x9D: "Y",  # output relay
    0x90: "M",  # internal relay
    0x92: "L",  # latch relay
    0x93: "F",  # annunciator
    0x94: "V",  # edge relay
    0xA0: "B",  # link relay
    0xC1: "TS", # timer contact
    0xC0: "TC", # timer coil
    0xC7: "SS", # retentive timer contact
    0xC6: "SC", # retentive timer coil
    0xC4: "CS", # counter contact
    0xC3: "CC", # counter coil
    0xA1: "SB", # link special relay
    0x98: "S",  # step relay
    0xA2: "DX", # direct access input
    0xA3: "DY", # direct access output
}

WORD_DEVICES = {
    0xA9: "SD", # special register
    0xA8: "D",  # data register
    0xB4: "W",  # link register
    0xC2: "TN", # timer current value
    0xC8: "SN", # retentive timer current value
    0xC5: "CN", # counter current value
    0xB5: "SW", # link special register
    0xCC: "Z",  # index register
    0xAF: "R",  # file register
    0xB0: "ZR", # file register (serial number access)
}


class ReusableTCPServer(TCPServer):
    allow_reuse_address = True


class ReusableUDPServer(UDPServer):
    allow_reuse_address = True


class FuncInc:
    def __init__(self):
        self.counter = 0

    def inc(self, delta=1):
        self.counter += delta
        return self.counter


class SLMPServerProcess:

    def server_process(self, opt):
        self.opt = opt

        if opt.enable_ascii:
            # 元コードにも ASCII モードがありますが、厳密な ASCII フレーム応答までは
            # 今回の改造対象外にしています。
            raise NotImplementedError("ASCII mode is not supported in this modified server.")

        self.hdr_len = 11
        client_name = "{}[{}]".format(*self.client_address)
        print(f"connected from {client_name}")

        while True:
            header = self.rfile.read(self.hdr_len)
            if len(header) == 0:
                break
            if len(header) != self.hdr_len:
                print(f"ERROR: short header: {len(header)} bytes")
                return

            (t_ver, reserved, net_num, pc_num, io_num, drop_num,
             length, m_timer) = self.parse_header_binary(header)

            # 3Eバイナリの length は通常、監視タイマ(2byte)以降ではなく、
            # 「監視タイマを含む要求データ長」です。
            # このコードでは監視タイマをヘッダ側で読み済みなので、
            # TCPで次のフレームとズレないよう、残りの書き込みデータ長を計算して
            # 必要分だけ読み捨てます。
            # lengthは監視タイマ(2 byte)を含む。監視タイマはヘッダとして
            # 読み込み済みなので、残りを要求データとして一括取得する。
            request_data_len = length - 2
            if request_data_len < 10:
                print(f"ERROR: rest data size {length} is too short")
                return

            request_data = self.rfile.read(request_data_len)
            if len(request_data) != request_data_len:
                print(f"ERROR: short request data: {len(request_data)} / {request_data_len} bytes")
                return

            try:
                (cmd, sub_cmd, dev_code, dev_num,
                 points, extra_data) = self.parse_request_binary(request_data)
            except ValueError as e:
                print(f"ERROR: {e}")
                self.response_error(net_num, pc_num, io_num, drop_num, 0xC059)
                continue

            if cmd == CMD_DEVICE_READ:
                if len(extra_data) > 0:
                    print(f"WARN: read command has unexpected extra data: {len(extra_data)} bytes")
                try:
                    self.response_read(net_num, pc_num, io_num, drop_num,
                                       sub_cmd, dev_code, dev_num, points)
                except ValueError as e:
                    print(f"ERROR: {e}")
                    self.response_error(net_num, pc_num, io_num, drop_num, 0xC059)
                continue

            if cmd == CMD_DEVICE_WRITE:
                self.response_write_accept(net_num, pc_num, io_num, drop_num,
                                           sub_cmd, dev_code, dev_num,
                                           points, extra_data)
                continue

            print(f"ERROR: unsupported cmd={cmd:04x}")
            self.response_error(net_num, pc_num, io_num, drop_num, 0xC059)

    def parse_header_binary(self, data):
        (t_ver, reserved, net_num, pc_num, io_num, drop_num,
         length, m_timer) = struct.unpack("<BBBBHBHH", data)

        print(f"t_type: {t_ver:x}")
        print(f"reserved: {reserved:x}")
        print(f"network: {net_num:02x}")
        print(f"pc_num: {pc_num:02x}")
        print(f"io_num: {io_num:04x}")
        print(f"drop_num: {drop_num:02x}")
        print(f"length: {length:04x}")
        print(f"m_timer: {m_timer:04x}")

        return (t_ver, reserved, net_num, pc_num, io_num, drop_num,
                length, m_timer)

    def parse_request_binary(self, data):
        if len(data) < 4:
            raise ValueError("command/subcommand is too short")

        cmd, sub_cmd = struct.unpack_from("<HH", data, 0)

        if sub_cmd in (SUBCMD_WORD_UNITS, SUBCMD_BIT_UNITS):
            # iQ-F/Q/L互換形式: デバイス番号3 byte + デバイスコード1 byte
            if len(data) < 10:
                raise ValueError("iQ-F/Q/L compatible request is too short")
            dev_num = int.from_bytes(data[4:7], "little")
            dev_code = data[7]
            points = struct.unpack_from("<H", data, 8)[0]
            extra_data = data[10:]
            frame_type = "iQ-F/Q/L compatible"
        elif sub_cmd in (SUBCMD_IQR_WORD_UNITS, SUBCMD_IQR_BIT_UNITS):
            # iQ-R形式: デバイス番号4 byte + デバイスコード2 byte
            if len(data) < 12:
                raise ValueError("iQ-R request is too short")
            dev_num = struct.unpack_from("<I", data, 4)[0]
            dev_code = struct.unpack_from("<H", data, 8)[0]
            points = struct.unpack_from("<H", data, 10)[0]
            extra_data = data[12:]
            frame_type = "iQ-R"
        else:
            raise ValueError(f"unsupported sub_cmd=0x{sub_cmd:04x}")

        dev_name = self.device_name(dev_code)

        print(f"cmd: {cmd:04x}")
        print(f"sub_cmd: {sub_cmd:04x}")
        print(f"device specification: {frame_type}")
        print(f"dev_code: {dev_code:04x} ({dev_name})")
        print(f"dev_num: {dev_num}")
        print(f"points: {points}")

        return (cmd, sub_cmd, dev_code, dev_num, points, extra_data)

    def is_bit_unit_subcommand(self, sub_cmd):
        return sub_cmd in (SUBCMD_BIT_UNITS, SUBCMD_IQR_BIT_UNITS)

    def is_word_unit_subcommand(self, sub_cmd):
        return sub_cmd in (SUBCMD_WORD_UNITS, SUBCMD_IQR_WORD_UNITS)

    def device_name(self, dev_code):
        if dev_code in BIT_DEVICES:
            return BIT_DEVICES[dev_code]
        if dev_code in WORD_DEVICES:
            return WORD_DEVICES[dev_code]
        return "unknown"

    def response_error(self, net_num, pc_num, io_num, drop_num, end_code):
        # 3E バイナリ応答
        # subheader(D000) + network + pc + io + station + data_length + end_code
        ret_data = []
        ret_data.append(b"\xD0\x00")
        ret_data.append(struct.pack("<BBHB", net_num, pc_num, io_num, drop_num))
        ret_data.append(struct.pack("<H", 2))
        ret_data.append(struct.pack("<H", end_code))
        self.wfile.write(b"".join(ret_data))

    def response_success_no_payload(self, net_num, pc_num, io_num, drop_num):
        # 正常終了だけを返す応答。書き込み受け入れ時に使います。
        ret_data = []
        ret_data.append(b"\xD0\x00")
        ret_data.append(struct.pack("<BBHB", net_num, pc_num, io_num, drop_num))
        ret_data.append(struct.pack("<H", 2))
        ret_data.append(struct.pack("<H", 0x0000))
        self.wfile.write(b"".join(ret_data))

    def response_write_accept(self, net_num, pc_num, io_num, drop_num,
                              sub_cmd, dev_code, dev_num, points, write_data):
        dev_name = self.device_name(dev_code)
        expected_len = self.expected_write_data_len(sub_cmd, dev_code, points)

        print("write accepted")
        print(f"write device: {dev_name}")
        print(f"write start: {dev_num}")
        print(f"write points: {points}")
        print(f"write data bytes: {len(write_data)}")
        if expected_len is not None and expected_len != len(write_data):
            print(f"WARN: write data size mismatch. expected={expected_len}, actual={len(write_data)}")
        print("write data is ignored. memory is not updated.")

        self.response_success_no_payload(net_num, pc_num, io_num, drop_num)

    def expected_write_data_len(self, sub_cmd, dev_code, points):
        # 厳密チェック用ではなく、ログ警告用の目安です。
        if points < 0:
            return None
        if dev_code in WORD_DEVICES:
            return points * 2
        if dev_code in BIT_DEVICES:
            if self.is_bit_unit_subcommand(sub_cmd):
                return (points + 1) // 2
            if self.is_word_unit_subcommand(sub_cmd):
                return points * 2
        return None

    def response_read(self, net_num, pc_num, io_num, drop_num,
                      sub_cmd, dev_code, dev_num, read_num):
        if read_num <= 0:
            raise ValueError("read_num must be greater than 0")

        if dev_code in WORD_DEVICES:
            payload = self.make_word_device_payload(read_num)
        elif dev_code in BIT_DEVICES:
            payload = self.make_bit_device_payload(sub_cmd, dev_num, read_num)
        else:
            raise ValueError(f"not supported dev_code=0x{dev_code:02x}")

        end_code = 0x0000
        data_length = 2 + len(payload)  # end_code + read data

        ret_data = []
        ret_data.append(b"\xD0\x00")
        ret_data.append(struct.pack("<BBHB", net_num, pc_num, io_num, drop_num))
        ret_data.append(struct.pack("<H", data_length))
        ret_data.append(struct.pack("<H", end_code))
        ret_data.append(payload)

        self.wfile.write(b"".join(ret_data))

    def make_word_device_payload(self, read_num):
        # D/W/R などは 1 点 = 1 word = 2 byte。
        payload = []
        for i in range(read_num):
            value = self.opt.func_resp_data(i) & 0xFFFF
            payload.append(struct.pack("<H", value))
        return b"".join(payload)

    def make_bit_device_payload(self, sub_cmd, dev_num, read_num):
        if self.is_bit_unit_subcommand(sub_cmd):
            return self.make_bit_unit_payload(dev_num, read_num)
        if self.is_word_unit_subcommand(sub_cmd):
            return self.make_bit_device_word_unit_payload(dev_num, read_num)
        raise ValueError(f"unsupported sub_cmd=0x{sub_cmd:04x} for bit device")

    def make_bit_unit_payload(self, dev_num, read_num):
        # ビット単位読み出しの場合、SLMP バイナリでは 1 byte に 2 点分を格納する。
        # 上位 4 bit が先頭側、下位 4 bit が次点側。
        # OFF/OFF = 0x00, OFF/ON = 0x01, ON/OFF = 0x10, ON/ON = 0x11
        payload = bytearray()
        i = 0
        while i < read_num:
            bit_1 = self.opt.func_resp_bit(dev_num + i) & 0x01
            if i + 1 < read_num:
                bit_2 = self.opt.func_resp_bit(dev_num + i + 1) & 0x01
            else:
                bit_2 = 0
            payload.append((bit_1 << 4) | bit_2)
            i += 2
        return bytes(payload)

    def make_bit_device_word_unit_payload(self, dev_num, read_num):
        # ビットデバイスをワード単位で読む場合、read_num は「ワード数」。
        # 1 word = 16 bit として、各 word を little endian で返す。
        payload = []
        for word_index in range(read_num):
            word_value = 0
            base = dev_num + word_index * 16
            for bit_index in range(16):
                bit_value = self.opt.func_resp_bit(base + bit_index) & 0x01
                word_value |= bit_value << bit_index
            payload.append(struct.pack("<H", word_value))
        return b"".join(payload)


class TCPHandler(StreamRequestHandler, SLMPServerProcess):
    def handle(self):
        self.server_process(opt)


class UDPHandler(DatagramRequestHandler, SLMPServerProcess):
    def handle(self):
        self.server_process(opt)


def build_value_function(func_type):
    if func_type == "c1":
        return lambda i: 1
    if func_type == "r10":
        return lambda i: int((i + time.time()) % 10)
    if func_type == "r100":
        return lambda i: int((i + time.time()) % 100)
    if func_type == "rand":
        return lambda i: int(random.random() * 100)
    if func_type == "inc":
        f = FuncInc()
        return lambda i: f.inc()
    raise ValueError(f"invalid func_type {func_type}")


def build_bit_function(bit_type):
    if bit_type == "c0":
        return lambda i: 0
    if bit_type == "c1":
        return lambda i: 1
    if bit_type == "alt":
        # 偶数番地 OFF、奇数番地 ON。
        return lambda i: i % 2
    if bit_type == "alt2":
        # 2 点ごとに OFF/OFF, ON/ON を繰り返す。
        return lambda i: (i // 2) % 2
    if bit_type == "rand":
        return lambda i: 1 if random.random() >= 0.5 else 0
    raise ValueError(f"invalid bit_type {bit_type}")


def add_ipv4_candidate(addresses, addr):
    """
    表示用のIPv4アドレス候補を追加します。

    ここで扱うのは「クライアント側に教える接続先IP」です。
    サーバのbindアドレス(opt.server_addr)とは別物です。
    """
    if not addr:
        return
    if addr.startswith("127."):
        return
    if addr.startswith("169.254."):
        return
    if addr == "0.0.0.0":
        return
    if addr not in addresses:
        addresses.append(addr)


def get_primary_local_ipv4():
    """
    OSのルーティング情報から、代表的なローカルIPv4アドレスを取得します。

    UDPソケットでconnectしていますが、UDPなのでこの時点で実パケットは
    送信されません。OSが「その宛先に出るなら、このローカルIPを使う」と
    判断したアドレスを getsockname() で取得します。
    """
    targets = [
        ("8.8.8.8", 80),        # 通常のデフォルトゲートウェイ確認用
        ("1.1.1.1", 80),        # 予備
        ("192.168.0.1", 80),    # 工場内LANなどで外部に出られない場合の予備
        ("192.168.1.1", 80),
    ]

    for target in targets:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(target)
            addr = sock.getsockname()[0]
            if addr and not addr.startswith("127."):
                return addr
        except OSError:
            pass
        finally:
            if sock is not None:
                sock.close()

    return None


def get_local_ip_candidates():
    """
    LAN内の別PC/PLCクライアントから接続するときに使えそうな
    ローカルIPv4アドレス候補を返します。

    重要：
      opt.server_addr は「待ち受けに使うbindアドレス」です。
      0.0.0.0 や 127.0.0.1 の場合があるため、接続先として表示する
      IPアドレスには使いません。

    この関数では socket / hostname / ipconfig から、実際のNICに
    割り当てられているIPv4アドレスを探します。
    """
    addresses = []

    # 方法1：OSのルーティング情報から代表IPを取得。
    primary = get_primary_local_ipv4()
    add_ipv4_candidate(addresses, primary)

    # 方法2：ホスト名から引けるIPv4を取得。
    try:
        hostname = socket.gethostname()
        infos = socket.getaddrinfo(hostname, None, socket.AF_INET)
        for info in infos:
            add_ipv4_candidate(addresses, info[4][0])
    except OSError:
        pass

    # 方法3：Windowsなら ipconfig から IPv4 アドレスを拾う。
    # 複数NICがある場合は、この方法が一番拾いやすいことがあります。
    try:
        output = subprocess.check_output(
            "ipconfig",
            shell=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
        text = output.decode("cp932", errors="ignore")
        for addr in re.findall(r"(?:IPv4[^:]*|IPv4 Address[^:]*):\s*([0-9]+(?:\.[0-9]+){3})", text):
            add_ipv4_candidate(addresses, addr)
    except Exception:
        pass

    return addresses


def print_server_addresses(protocol, bind_addr, port):
    """
    起動時に、待ち受け情報と接続先候補を表示します。

    bind_addr:
      サーバが待ち受けるアドレスです。
      0.0.0.0 は「全NICで待ち受ける」という意味で、クライアントが
      接続先として指定するIPアドレスではありません。

    connect address candidates:
      socketなどから取得した、このPCのローカルIPv4アドレスです。
      別PC/PLCクライアント側には、通常はこちらを設定します。
    """
    print(f"listening on {protocol} bind={bind_addr} port={port}")

    candidates = get_local_ip_candidates()

    if bind_addr in ("0.0.0.0", ""):
        print("connect address candidates from this PC:")
        if candidates:
            for addr in candidates:
                print(f"  {addr}:{port}")
        else:
            print("  local IP was not detected automatically.")
            print("  Please check with ipconfig, then connect to that IPv4 address.")
        print(f"  same PC only: 127.0.0.1:{port}")
        return

    if bind_addr.startswith("127."):
        print(f"connect address: 127.0.0.1:{port}")
        print("NOTE: 127.0.0.1 is loopback. Other PCs/PLC clients cannot connect to it.")
        if candidates:
            print("local IP candidates detected by socket/ipconfig:")
            for addr in candidates:
                print(f"  {addr}:{port}")
            print("NOTE: To accept LAN connections, start with: -s 0.0.0.0")
        return

    print(f"connect address: {bind_addr}:{port}")
    if candidates and bind_addr not in candidates:
        print("other local IP candidates detected by socket/ipconfig:")
        for addr in candidates:
            print(f"  {addr}:{port}")


def main():
    global opt

    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--udp", action="store_true", dest="enable_udp",
                    help="enable UDP mode. default is TCP.")
    ap.add_argument("-t", "--tcp", action="store_true", dest="enable_tcp",
                    help="enable TCP mode. TCP is default, so this option is optional.")
    ap.add_argument("-4", action="store_true", dest="enable_4E",
                    help="display only. 4E frame is not implemented.")
    ap.add_argument("-a", "--ascii", action="store_true", dest="enable_ascii",
                    help="ASCII mode is not supported in this modified server.")
    ap.add_argument("-s", "--server-addr", action="store", dest="server_addr",
                    default="0.0.0.0",
                    help="server bind address. default: 0.0.0.0")
    ap.add_argument("-p", "--port", action="store", dest="server_port",
                    type=int, default=10000,
                    help="server port number. default: 10000")
    ap.add_argument("-F", "--func", action="store", dest="func_type",
                    default="r100", choices=["c1", "r10", "r100", "rand", "inc"],
                    help="word response value generator. default: r100")
    ap.add_argument("-B", "--bit-func", action="store", dest="bit_type",
                    default="alt", choices=["c0", "c1", "alt", "alt2", "rand"],
                    help="bit response value generator. default: alt")
    opt = ap.parse_args()

    opt.func_resp_data = build_value_function(opt.func_type)
    opt.func_resp_bit = build_bit_function(opt.bit_type)

    if opt.enable_udp:
        ServerClass = ReusableUDPServer
        HandlerClass = UDPHandler
    else:
        ServerClass = ReusableTCPServer
        HandlerClass = TCPHandler

    server = ServerClass((opt.server_addr, opt.server_port), HandlerClass)

    print_server_addresses("UDP" if opt.enable_udp else "TCP",
                           opt.server_addr, opt.server_port)
    print("{} {}".format("4E" if opt.enable_4E else "3E",
                          "ASCII" if opt.enable_ascii else "BINARY"))
    print("device formats: iQ-F/Q/L compatible and iQ-R")
    print("word func: {}".format(opt.func_type))
    print("bit func: {}".format(opt.bit_type))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    except Exception as e:
        print("ERROR", e)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

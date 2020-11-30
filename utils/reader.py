import io


class Reader:
	def __init__(self, data):
		self.stream = io.BytesIO(data)

	def read_byte(self):
		return int.from_bytes(self.stream.read(1), 'little')

	def read_uint16(self):
		return int.from_bytes(self.stream.read(2), 'little')

	def read_int16(self):
		return int.from_bytes(self.stream.read(2), 'little', signed=True)

	def read_uint32(self):
		return int.from_bytes(self.stream.read(4), 'little')

	def read_int32(self):
		return int.from_bytes(self.stream.read(4), 'little', signed=True)

	def read_int64(self):
		return int.from_bytes(self.stream.read(8), 'little', signed=True)

	def read_char(self, length: int = 1) -> str:
		return self.stream.read(length).decode('utf-8')

	def read_string(self) -> str:
		length = self.read_uint16()
		return self.read_char(length)

	def read_string_little(self) -> str:
		buffer = b''
		while True:
			readByte = self.read(1)
			if readByte == b"\x00":
				break
			else:
				buffer += readByte
		return buffer.decode()

	def skip(self, num):
		for i in range(0, num):
			self.read_byte()

	def set_offset(self, offset):
		self.stream.seek(offset)

	def read(self, size):
		return self.stream.read(size)

	def read_hash(self, size) -> str:
		data = self.stream.read(size)
		hash = ""
		for b in data:
			hash += "%02x" % b
		return hash



from parsers import CSVParser, ThreadedCSVParser


parser = ThreadedCSVParser(1, "ip_address", "username", "password")
result = parser.parse("Test.csv")
print(result)
import json
from csv import DictWriter
dicts = json.loads(data)
the_file = open("sample.csv", "w")
writer = DictWriter(the_file, dicts[0].keys())
writer.writeheader()
writer.writerows(dicts)
the_file.close()
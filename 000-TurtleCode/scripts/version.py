f = open("version.txt", "r")
_VERSION_ = int(f.read())
f.close()
f = open("version.txt", "w+")
f.write(str(_VERSION_+1))
f.close()


def get_version_num():
    return _VERSION_

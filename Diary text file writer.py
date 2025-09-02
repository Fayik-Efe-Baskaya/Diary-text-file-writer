class Diary:
    from os import rename, remove, path

    def __init__(self, name, path):
        self.day = 1
        self.name = name
        self.path = path
        if Diary.path.exists(f"{Diary.path.join(self.path, self.name)}.txt"):
            raise ValueError("This file already exists!")

    def new(self, writings = ""):
        with open(f"{Diary.path.join(self.path, self.name)}.txt", "a", encoding = "cp1254") as d:
            d.write(f"DAY {self.day}\n{writings}\n\n")
            self.day += 1

    def read(self, character = 0):
        with open(f"{Diary.path.join(self.path, self.name)}.txt", "r", encoding="cp1254") as d:
            w = d.read()

            if character + 1 > len(w):
                raise ValueError
            return w[character:]

    def read_line(self, line = 0):
        with open(f"{Diary.path.join(self.path, self.name)}.txt", "r", encoding="cp1254") as d:
            l = d.readlines()

            if line + 1 > len(l):
                raise ValueError
            return l[line]

    def delete_day(self, day):
        with open(f"{Diary.path.join(self.path, self.name)}.txt", "r+", encoding="cp1254") as d:
            l = d.readlines()
            d.seek(0)

            try:
                fd = l.index(f"DAY {day}\n")
            except ValueError:
                return
            d.seek(0)

            if not f"DAY {day + 1}\n" in l:
                del l[fd:]
                d.seek(0)
                d.truncate()
                d.writelines(l)
            else:
                ld = d.readlines().index(f"DAY {day + 1}\n")
                d.seek(0)
                del l[fd:ld]
                d.seek(0)
                d.truncate()
                d.writelines(l)

    def change_name(self, new):
        if Diary.path.exists(f"{Diary.path.join(self.path, new)}.txt"):
            raise ValueError("This file already exists!")
        else:
            fn = f"{Diary.path.join(self.path, self.name)}.txt"
            self.name = new
            ln = f"{Diary.path.join(self.path, self.name)}.txt"

            Diary.rename(fn, ln)

    def change_path(self, new):
        if Diary.path.exists(f"{Diary.path.join(self.path, new)}.txt"):
            raise ValueError("This file already exists!")
        else:
            fp = f"{Diary.path.join(self.path, self.name)}.txt"
            self.path = new
            lp = f"{Diary.path.join(self.path, self.name)}.txt"

            Diary.rename(fp, lp)

    def delete_file(self):
        Diary.remove(f"{Diary.path.join(self.path, self.name)}.txt")
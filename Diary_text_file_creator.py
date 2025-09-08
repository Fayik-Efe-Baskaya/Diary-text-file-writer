from os import rename, remove, path

from time import sleep, strftime

from functools import wraps

from re import sub

import sqlite3 as sql

diarydb = sql.connect("diary.db")

diaryd = diarydb.cursor()
diaryd.execute("CREATE TABLE IF NOT EXISTS Diaries (path, day INT)")

class Diary:
    def __init__(self, name, fpath):
        self.name = name
        self.fpath = fpath
        if path.exists(f"{path.join(self.fpath, self.name)}.txt"):
            print("Reminder: This file already exists. Therefore we do not create a file. You can take operations on that file instead.")
        else:
            n = f"{sub(r'\W', '', self.fpath)}{self.name}"
            diaryd.execute(f"INSERT INTO Diaries VALUES ('{path.join(self.fpath, self.name)}', 1)")
            diaryd.execute(f"CREATE TABLE IF NOT EXISTS {n} (operations)")
            diarydb.commit()
            with open(f"{path.join(self.fpath, self.name)}.txt", "w", encoding = "utf-8"):
                pass

    @staticmethod
    def operations(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            n = f"{sub(r'\W', '', self.fpath)}{self.name}"
            diaryd.execute(f"INSERT INTO {n} VALUES ('{func.__name__} operation was taken on"
                           f"{strftime('%m/%d/%Y')} at {strftime('%H:%M')}')")
            diarydb.commit()
            return func(self, *args, **kwargs)
        return wrapper

    def show_operations(self):
        n = f"{sub(r'\W', '', self.fpath)}{self.name}"
        for o in diaryd.execute(f"SELECT * FROM {n}"):
            print(o)

    @operations
    def write_new_day(self, writings = ""):
        with open(f"{path.join(self.fpath, self.name)}.txt", "a", encoding = "utf-8") as d:
            d.write(f"DAY {diaryd.execute(f"SELECT day FROM Diaries WHERE path = '{path.join(self.fpath, self.name)}'").fetchone()[0]}"
                    f"\n{writings}\n\n")
            diaryd.execute(f"UPDATE Diaries SET day = day + 1 WHERE path = '{path.join(self.fpath, self.name)}'")
            diarydb.commit()

    @operations
    def read_the_file(self):
        with open(f"{path.join(self.fpath, self.name)}.txt", "r", encoding = "utf-8") as d:
            w = d.read()
            d.seek(0)
            return w

    @operations
    def read_a_day(self, day):
        with open(f"{path.join(self.fpath, self.name)}.txt", "r", encoding = "utf-8") as d:
            l = d.readlines()
            d.seek(0)

            try:
                day = int(day)
            except ValueError:
                return "Invalid day value!"

            if f"DAY {int(day)}\n" not in l:
                return "Invalid day value!"
            if f"DAY {int(day) + 1}\n" not in l:
                d.seek(0)
                return "\n".join(l[l.index(f"DAY {int(day)}"):])
            return "\n".join(l[l.index(f"DAY {int(day)}\n"):l.index(f"DAY {int(day) + 1}\n")])

    @operations
    def delete_a_day(self, day):
        with open(f"{path.join(self.fpath, self.name)}.txt", "r+", encoding = "utf-8") as d:
            l = d.readlines()
            d.seek(0)

            try:
                day = int(day)
            except ValueError:
                print("Invalid day value!")
                return

            if f"DAY {int(day)}\n" not in l:
                print("Invalid day value!")

            fd = l.index(f"DAY {int(day)}\n")
            d.seek(0)

            if not f"DAY {int(day) + 1}\n" in l:
                del l[fd:]
                d.seek(0)
                d.truncate()
                d.writelines(l)
            else:
                ld = d.readlines().index(f"DAY {int(day) + 1}\n")
                d.seek(0)
                del l[fd:ld]
                d.seek(0)
                d.truncate()
                d.writelines(l)

    @operations
    def change_name_of_the_file(self, new):
        if any(c in [':', '*', '?', '""', '<', '>', '|'] for c in new):
            print("Your file name includes invalid characters!")

        if path.exists(f"{path.join(new, self.fpath)}.txt"):
            print("There is a file with the same name in that path!")
            return
        fn = f"{path.join(self.fpath, self.name)}.txt"
        self.name = new
        ln = f"{path.join(self.fpath, self.name)}.txt"

        rename(fn, ln)
        diaryd.execute(f"UPDATE Diaries SET path = '{path.join(self.fpath, new)}' WHERE path = '{path.join(self.fpath, self.name)}'")
        diarydb.commit()

    @operations
    def change_path_of_the_file(self, new):
        from shutil import move

        if any(c in ['/', '*', '?', '"', '<', '>', '|'] for c in new):
            print("Your file path includes invalid characters!")

        if path.exists(f"{path.join(new, self.fpath)}.txt"):
            print("There is a file with the same name in that path!")
            return
        fp = f"{path.join(self.fpath, self.name)}.txt"
        self.fpath = new
        lp = f"{path.join(self.fpath, self.name)}.txt"

        move(fp, lp)
        diaryd.execute(f"UPDATE Diaries SET path = '{path.join(sub(r'\W', '', new), self.name)}'"
                       f" WHERE path = '{path.join(self.fpath, self.name)}'")
        diarydb.commit()

    @operations
    def delete_the_file(self):
        n = f"{sub(r'\W', '', self.fpath)}{self.name}"
        remove(f"{path.join(self.fpath, self.name)}.txt")
        diaryd.execute(f"DELETE FROM {n}")
        diaryd.execute(f"DELETE FROM Diaries WHERE path = '{path.join(self.fpath, self.name)}'")
        diarydb.commit()

def main():
    from os import path

    print("-------------------------Welcome to the diary text file creator!-------------------------")

    while True:
        file_name = input("Please enter the name of your file (Enter 'x' to exit the program): ")
        if any(c in [':', '*', '?', '""', '<', '>', '|'] for c in file_name):
            print("Your file name includes invalid characters!")
            sleep(1.5)
            continue
        if file_name.lower() == "x":
            return

        file_path = input("Please enter the path of your file (press enter to use your 'Users/username' directory)"
                          "(Enter 'x' to exit the program): ")
        if file_path == "":
            file_path = path.expanduser("~")
        elif any(c in ['/', '*', '?', '"', '<', '>', '|'] for c in file_path):
            print("Your file path includes invalid characters!")
            sleep(1.5)
            continue
        elif file_path.lower() == "x":
            return
        elif not path.exists(file_path):
            print("Your file path not found!")
            sleep(1.5)
            continue

        if path.exists(f"{path.join(file_path, file_name)}.txt"):
            if diaryd.execute(f"SELECT 1 FROM Diaries WHERE path = '{path.join(file_path, file_name)}'").fetchone():
                diary = Diary(file_name, file_path)
            else:
                print("This file had been created manually. Delete this file or enter a new file path.")
                continue
        else:
            if diaryd.execute(f"SELECT 1 FROM Diaries WHERE path = '{path.join(file_path, file_name)}'").fetchone():
                diaryd.execute(f"DELETE FROM Diaries WHERE path = '{path.join(file_path, file_name)}'")
                diarydb.commit()
            diary = Diary(file_name, file_path)

        while True:
            sleep(1.5)
            choice = input(
                "1-Write a new day\n2-Read the file\n3-Read a day\n4-Delete a day\n5-Change the file path\n6-Change the file name\n"
                "7-Delete the file\n8-Show the operations that were taken\nx-Back to the entering file name\n"
                "Enter the number of your selection: ")

            if choice == "1":
                new = input("Write a new day: ")
                diary.write_new_day(new)
                continue

            elif choice == "2":
                print(diary.read_the_file())
                continue

            elif choice == "3":
                day = input("Enter the day that is going to be read: ")

                print(diary.read_a_day(day))
                continue

            elif choice == "4":
                day = input("Enter the day that is going to be deleted: ")

                diary.delete_a_day(day)
                continue

            elif choice == "5":
                new = input("Enter the new path of the file: ")

                diary.change_path_of_the_file(new)
                continue

            elif choice == "6":
                new = input("Enter the new name of the file: ")

                diary.change_name_of_the_file(new)
                continue

            elif choice == "7":
                diary.delete_the_file()
                continue

            elif choice == "8":
                diary.show_operations()
                continue

            elif choice.lower() == "x":
                break

            else:
                print("Invalid choice!")
                continue
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("UNEXPECTED ERROR", e)
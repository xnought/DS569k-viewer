import os
import subprocess
import shutil


class Executable:
    def __init__(self, path):
        if not os.path.exists(path):
            raise ImportError(f"Could not find {path}")
        self.path = path

    def __call__(self, cmd=""):
        return subprocess.check_output(f"{self.path} {cmd}", shell=True).decode()

    def __repr__(self):
        return f"Executable(path='{self.path}')"


class Foldseek(Executable):
    def __init__(self, executable):
        super().__init__(executable)
        self.temp_dir = os.path.join(".", "temp")
        self.out_file = os.path.join(self.temp_dir, "output")

    def _delete_temp(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _parse_out_file(self):
        with open(self.out_file, "r") as f:
            lines = f.readlines()
            parsed_lines = []
            for line in lines:
                parsed_line = []
                for column in line.strip("\n").split("\t"):
                    try:
                        column = float(column)
                    except ValueError:
                        pass
                    parsed_line.append(column)
                parsed_lines.append(parsed_line)

            return parsed_lines

    def search(
        self, query, target, flags="--format-output query,target,prob", clean=True
    ):
        search_out = None
        try:
            stdout = self(
                f"easy-search {query} {target} {self.out_file} {self.temp_dir} {flags}"
            )
            search_out = self._parse_out_file()
        except Exception as e:
            print(e)

        if clean:
            self._delete_temp()

        return search_out

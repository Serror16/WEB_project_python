import os
import typer

app = typer.Typer()

def show_dir_tree(dir: str, tabs: int, f1, full: bool = False) -> None:
    f1.write(f"{"\t"*tabs}{os.path.basename(dir)}\\\n".replace("\\", "/"))
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        if os.path.isdir(path):
            show_dir_tree(path, tabs+1, f1)
        else:
            f1.write(f"{"\t"*(tabs+1)}{file}\n")
            # with open(path, "r", encoding="utf-8") as f:
            #     for i in f.readlines():
            #         f1.write(f"{"\t"*(tabs+1)}{i}")



@app.command()
def show(
    path: str = typer.Argument(default=None),
    full: bool = typer.Option(False, "-f", "--full")
) -> None:
    f1 = open("test.txt", "w")
    show_dir_tree(path, 0, f1, full)



app()
import typer
import requests
from requests.exceptions import ConnectionError
from rich.console import Console
from rich.style import Style

app = typer.Typer()

console = Console()
strike_style = Style(strike=True)  

API_BASE = "http://127.0.0.1:8000"

def check_connection():
    try:
        requests.get(f"{API_BASE}/todo/ping")
    except ConnectionError:
        print("сервер не отвечает")
        raise typer.Exit(code=1)

@app.command()
def list():
    '''получить все задачи'''
    check_connection()
    r = requests.get(f"{API_BASE}/todo/get/all")
    tasks = r.json()

    complited_tasks = tasks['complite']
    incomplited_tasks = tasks['incomplite']

    console.print("\n////---TODO---////",style='#f5df4d')
    console.print('------------------',style='#939597')
    console.print("\nактуальные задачи:",style='#45b5aa')

    for task in incomplited_tasks:
        status = "+" if task['complite'] else "-"
        console.print(f"{task['id']}: {task['name']} ({task['date']}) {status}")

    console.print('\n------------------',style='#939597')
    console.print("выполненные задачи:",style='#45b5aa')

    for task in complited_tasks:
        status = "+" if task['complite'] else "-"
        console.print(f"{task['id']}: [strike]{task['name']}[/strike] ({task['date']}) {status}")
    
    console.print('')

@app.command()
def add(name: str):
    '''добавить новую задачу'''
    check_connection()
    r = requests.get(f"{API_BASE}/todo/create/{name}")
    console.print(r.text)

@app.command()
def get(id: int):
    '''получить задачу по переданному id'''
    check_connection()
    r = requests.get(f"{API_BASE}/todo/get", params={"id":id})
    if r.status_code == 404:
        console.print("задача не найдена")
    else:
        task = r.json()
        status = "+" if task['complite'] else "-"
        console.print(f"{task['id']}: {task['name']} ({task['date']}) {status}")

@app.command()
def delete(id: int):
    '''удалить задачу по переданному id'''
    check_connection()
    r = requests.delete(f"{API_BASE}/todo/delete", params={"id": id})
    console.print(f"задача {id} удалена")

@app.command()
def status(id: int):
    '''обновить статус задачи'''
    check_connection()
    r = requests.get(f"{API_BASE}/todo/status", params={"id": id})
    console.print("mission complited.")

def main():
    app()


if __name__ == "__main__":
    app()

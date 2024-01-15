# Imports
from datetime import datetime, timedelta
from math import floor
from pathlib import Path
import flet as ft
import pandas as pd

# Task details
task_dets = {
    "slot": None,
    "start": None,
    "end": None,
    "title": None,
    "desc": None,
    "priority": None,
    "tid": None,
    "pre_tid": None,
    "post_tid": None,
}
tcols = list(task_dets.keys())

# Reading or creating today's schedule
# Path manipulations
SCHEDULES_DIR = Path("./Schedules")
SCHEDULES_DIR.mkdir(exist_ok=True)  # For first runs
# all_schedules = SCHEDULES_DIR.glob("*.xlsx")

# Date and time dealings
date_format = "%m-%d-%y"
time_format = "%H:%M"
today = datetime.date(datetime.now()).strftime(date_format)
sch_file = SCHEDULES_DIR / (today + ".xlsx")
DAY_START = datetime.strptime("09:00", time_format)  # 09:00 HRS
DAY_END = datetime.strptime("18:00", time_format)  # 18:00 HRS
num_slots = int(floor((DAY_END - DAY_START).total_seconds() / (60 * 60)))

# File manipulations
try:  # User is expected to make a copy of the excel sheet template with name "MM-DD-YY.xlsx" and enter tasks into it
    schedule = pd.read_excel(sch_file).reset_index().drop(["Unnamed: 0", "index"], axis=1)
except FileNotFoundError:  # Creates the template excel file
    schedule = pd.DataFrame(columns=tcols)
    schedule["slot"] = pd.Series(range(1, num_slots + 1))
    schedule["start"] = pd.Series(
        [(DAY_START + timedelta(hours=i)).strftime(time_format) for i in range(0, num_slots + 1)]
    )
    schedule["end"] = pd.Series(
        [(DAY_START + timedelta(hours=i)).strftime(time_format) for i in range(1, num_slots + 2)]
    )
    schedule.to_excel(sch_file)

class Task(ft.UserControl):
    def __init__(self, task_name, task_status_change, task_delete, task_details):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.task_details = task_details

        self.slot = task_details["slot"] if task_details["slot"] else 0
        self.start = task_details["start"] if task_details["start"] else 0
        self.end = task_details["end"] if task_details["end"] else 0
        self.desc = task_details["desc"] if task_details["desc"] else ""
        self.priority = task_details["priority"] if task_details["priority"] else 0
        self.tid = task_details["tid"] if task_details["tid"] else 0
        self.pre_tid = task_details["pre_tid"] if task_details["pre_tid"] else 0
        self.post_tid = task_details["post_tid"] if task_details["post_tid"] else 0
        self.pcolors = {1: ft.colors.RED, 2: ft.colors.ORANGE, 3: ft.colors.YELLOW, 4: ft.colors.GREEN, 5: ft.colors.BLACK}

    def build(self):
        # self.display_task = ft.Checkbox(
        #     value=False, label=self.task_name, on_change=self.status_changed
        # )
        self.display_task = ft.Column(
            controls=[
                ft.Text(f"Task name: {self.task_name}", color=self.pcolors[self.priority]),
                ft.Text(f"Description: {self.desc}"),
                ft.ListTile(title=ft.Text(f"Start time: {self.start}")),
                ft.ListTile(title=ft.Text(f"End time: {self.end}")),
                ft.ListTile(title=ft.Text(f"Priority: {self.priority}")),
                ft.ListTile(title=ft.Text(f"Task ID: {self.tid}")),
                ft.ListTile(title=ft.Text(f"Predecessor ID: {self.pre_tid}")),
                ft.ListTile(title=ft.Text(f"Successor ID: {self.post_tid}")),
                ft.Checkbox(value=False, label="Finished?", on_change=self.status_changed),
                ft.Divider(thickness=3,color=ft.colors.BLUE_ACCENT)
                ]
                    )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete task",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )
        return ft.Column(controls=[self.display_view])

    async def status_changed(self, e):
        self.completed = self.display_task.controls
        await self.task_status_change(self)

    async def delete_clicked(self, e):
        await self.task_delete(self)


class TodoApp(ft.UserControl):
    def build(self):
        self.new_task = ft.Text("Fetch today's schedule from excel!")
        self.tasks = ft.Column()

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="All"), ft.Tab(text="Active"), ft.Tab(text="Completed")],
        )

        self.items_left = ft.Text("0 items left")

        # application's root control (i.e. "view") containing all other controls
        return ft.Column(
            width=700,
            controls=[
                ft.Row(
                    [ft.Text(value="Tasks for the day!", style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(
                            icon=ft.icons.DOWNLOAD, on_click=self.add_clicked
                        ),
                    ],
                ),
                ft.Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.items_left,
                                ft.OutlinedButton(
                                    text="Clear completed", on_click=self.clear_clicked
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    async def add_clicked(self, e):
        if len(schedule) > 0:
            # task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            # self.tasks.controls.append(task)
            # self.new_task.value = ""
            tasks = []
            for i in range(len(schedule)):
                t = Task(task_name=schedule["title"][i], task_status_change=self.task_status_change, task_delete=self.task_delete, task_details=dict(schedule.iloc[i]))
                tasks.append(t)
            self.tasks.controls.extend(tasks)
            # await self.new_task.focus_async()
            await self.update_async()
        else:
            task = Task("Create schedule first in excel!", self.task_status_change, self.task_delete, task_details=task_dets)
            self.tasks.controls.append(task)
            await self.new_task.focus_async()
            await self.update_async()


    async def task_status_change(self, task):
        await self.update_async()

    async def task_delete(self, task):
        self.tasks.controls.remove(task)
        await self.update_async()

    async def tabs_changed(self, e):
        await self.update_async()

    async def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                await self.task_delete(task)

    async def update_async(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "All"
                or (status == "Active" and task.completed == False)
                or (status == "Completed" and task.completed)
            )
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} active item(s) left"
        await super().update_async()


async def main(page: ft.Page):
    page.title = "Schedule for the day!"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    # create app control and add it to the page
    await page.add_async(TodoApp())


ft.app(main)
# Imports
from datetime import datetime
import json
import flet as ft


class Task(ft.UserControl):
    def __init__(self, task_name, task_status_change, task_delete, task_dets):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

        self.start = task_dets["start"] if task_dets["start"] else 0
        self.end = task_dets["end"] if task_dets["end"] else 0
        self.desc = task_dets["desc"] if task_dets["desc"] else ""
        self.priority = task_dets["priority"] if task_dets["priority"] else 0
        self.tid = task_dets["tid"] if task_dets["tid"] else 0
        self.pre_tid = task_dets["pre_tid"] if task_dets["pre_tid"] else 0
        self.post_tid = task_dets["post_tid"] if task_dets["post_tid"] else 0
        self.pcolors = {"1": ft.colors.RED, "2": ft.colors.ORANGE, "3": ft.colors.YELLOW, "4": ft.colors.GREEN, "5": ft.colors.BLACK}

    def build(self):
        self.display_task = ft.ExpansionTile(
            title=ft.Text(self.task_name),
            maintain_state=True,
            affinity=ft.TileAffinity.PLATFORM,
            text_color=self.pcolors[self.priority],
            controls=[
                ft.Text(value=self.desc),
                ft.ListTile(title=ft.Text(value=f"Start time: {self.start}")),
                ft.ListTile(title=ft.Text(value=f"End time: {self.end}")),
                ft.ListTile(title=ft.Text(value=f"Priority: {self.priority}")),
                ft.ListTile(title=ft.Text(value=f"Task ID: {self.tid}")),
                ft.ListTile(title=ft.Text(value=f"Predecessor ID: {self.pre_tid}")),
                ft.ListTile(title=ft.Text(value=f"Successor ID: {self.post_tid}")),
                ft.Checkbox(value=False, label=self.task_name, on_change=self.status_changed),
                ]
                    )

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
                            tooltip="Delete Task",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )
        return self.display_view


    async def status_changed(self, e):
        self.completed = self.display_task.value
        await self.task_status_change(self)

    async def delete_clicked(self, e):
        await self.task_delete(self)


class TodoApp(ft.UserControl):

    def pick_time(self, sen):
        time_picker = ft.TimePicker(
            confirm_text="Confirm",
            error_invalid_text="Time out of range",
            help_text=f"Select '{sen}'-time",
            on_change=lambda e: self.task_dets.update({f"{sen}": e.value}),
            on_dismiss=lambda e: self.task_dets.update({f"{sen}": e.value}),
        )
        return time_picker
    
    def taskview(self, tasks):
        tv = ft.Column(
            width=700,
            controls=[
                ft.Row(
                    [ft.Text(value="Today's schedule!", style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Column(
                    spacing=25,
                    controls=[
                        tasks,
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
            ]
        )
        return tv
    
    def build(self):
        self.task_dets = {
        "start": None,
        "end": None,
        "title": None,
        "desc": None,
        "priority": None,
        "tid": None,
        "pre_tid": None,
        "post_tid": None
    }
        self.new_task = ft.Text("Hit the plus button to add a task!")
        self.new_task_f = ft.Column(width=700, controls=[
            ft.TextField(hint_text="Task Name", expand=True, on_submit=lambda e: self.task_dets.update({"title": e.value})),
            ft.TextField(hint_text="Task Description", expand=True, on_submit=lambda e: self.task_dets.update({"desc": e.value})),
            ft.Row(controls=[ft.Text("Priority: "), ft.SegmentedButton(selected_icon=ft.Icon(ft.icons.CHECK), on_change=lambda e: self.task_dets.update({"priority": e.data}),
                               segments=[ft.Segment(label=ft.Text("1"), value="1"), ft.Segment(label=ft.Text("2"), value="2"), 
                                        ft.Segment(label=ft.Text("3"), value="3"), ft.Segment(label=ft.Text("4"), value="4"),
                                        ft.Segment(label=ft.Text("5"), value="5")]) ]),
            ft.TextField(hint_text="Task ID - Must be unique number", expand=True, on_submit=lambda e: self.task_dets.update({"tid": e.value})),
            ft.TextField(hint_text="Predecessor ID - Task to be done before this", expand=True, on_submit= lambda e: self.task_dets.update({"pre_tid": e.value})),
            ft.TextField(hint_text="Successor ID - Task to be done after this", expand=True, on_submit=lambda e: self.task_dets.update({"post_tid": e.value})),
            ft.ElevatedButton(text="Set Start Time", on_click=lambda e: self.pick_time("start")),
            ft.ElevatedButton(text="Set End Time", on_click=lambda e: self.pick_time("end")),
            ft.ElevatedButton(text="Add Task", on_click=self.add_clicked)
        ])
        self.completed_tasks = ft.Column()
        self.pending_tasks = ft.Column()
        self.tasks = ft.Column()
        self.items_left = ft.Text("0 items left")
        self.tabview = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="New task", content=self.new_task_f),
                  ft.Tab(text="All", content=self.taskview(self.tasks)),
                  ft.Tab(text="Incomplete", content=self.taskview(self.pending_tasks)),
                  ft.Tab(text="Completed", content=self.taskview(self.completed_tasks))],
        )
        return self.tabview

    async def add_clicked(self, e):
        task = Task(self.task_dets["title"], self.task_status_change, self.task_delete, self.task_dets)
        self.tasks.append(task)
        await self.update_async()

    async def task_status_change(self, task):
        await self.update_async()

    async def task_delete(self, task):
        self.tasks.remove(task)
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
    page.title = "Matt Assist!"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    # create app control and add it to the page
    await page.add_async(TodoApp())

ft.app(main)
import flet as ft

def main(page: ft.Page):

    # カウンター表示用テキスト
    counter = ft.Text("0", size=50, data=0)

    # プラスボタンの処理
    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()

    # マイナスボタンの処理
    def decrement_click(e):
        counter.data -= 1
        counter.value = str(counter.data)
        counter.update()

    # 右下のプラスボタン
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=increment_click
    )

    # 左下のマイナスボタン
    minus_button = ft.FloatingActionButton(
        icon=ft.Icons.REMOVE,
        on_click=decrement_click,
        bgcolor=ft.Colors.RED_400,
    )

    # FAB 位置仍然是右下角
    page.floating_action_button_location = ft.FloatingActionButtonLocation.END_FLOAT

    # 左下のマイナスボタンを配置
    page.add(
        ft.Row(
            [
                minus_button,
            ],
            alignment=ft.MainAxisAlignment.START,
        )
    )

    # カウンター本体
    page.add(
        ft.SafeArea(
            ft.Container(
                counter,
                alignment=ft.alignment.center,
            ),
            expand=True,
        )
    )

ft.app(main)

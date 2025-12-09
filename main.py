import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
import threading
import requests
import time
import traceback

# Налаштування вікна (не впливає на Android, але зручно для тестів на PC)
from kivy.core.window import Window
Window.clearcolor = (0.1, 0.1, 0.1, 1)

HOST = "http://192.168.8.1"

class ModemRebooterApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        self.label = Label(text="Huawei Modem Rebooter", size_hint=(1, 0.1), font_size='20sp')
        self.layout.add_widget(self.label)

        # Логи (вікно виводу)
        self.logs = TextInput(text="Готовий до роботи...\n", readonly=True, background_color=(0.2, 0.2, 0.2, 1), foreground_color=(0, 1, 0, 1), font_size='14sp')
        self.layout.add_widget(self.logs)

        # Кнопка запуску
        self.btn = Button(text="Перезавантажити Інтернет", size_hint=(1, 0.2), background_color=(0, 0.6, 1, 1), font_size='18sp')
        self.btn.bind(on_press=self.start_thread)
        self.layout.add_widget(self.btn)

        return self.layout

    def log(self, message):
        """Додає повідомлення у вікно логів"""
        # Оновлення UI має відбуватися в головному потоці
        Clock.schedule_once(lambda dt: self._update_log(message))

    def _update_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.text += f"[{timestamp}] {message}\n"

    def start_thread(self, instance):
        """Запускає логіку в окремому потоці"""
        self.btn.disabled = True
        self.log("Запуск процедури...")
        threading.Thread(target=self.run_script).start()

    def run_script(self):
        try:
            self.log(f"Підключення до {HOST}...")
            s = requests.Session()
            s.headers.update({"User-Agent": "Mozilla/5.0"})

            # 1. Отримуємо токен
            try:
                r = s.get(f"{HOST}/html/home.html", timeout=5)
                self.log(f"Статус сторінки: {r.status_code}")
            except Exception as e:
                self.log(f"Помилка підключення: {str(e)}")
                self.enable_btn()
                return

            token = ""
            if 'name="csrf_token"' in r.text:
                token = r.text.split('name="csrf_token" content="')[1].split('"')[0]
            elif 'Name="csrf_token"' in r.text:
                token = r.text.split('Name="csrf_token" Content="')[1].split('"')[0]
            else:
                try:
                    token = r.text.split('__RequestVerificationToken:')[1].split("'")[1]
                except:
                    pass

            if not token:
                self.log("ПОМИЛКА: Токен не знайдено! Перевірте модель модема.")
                self.log(f"Зміст відповіді (перші 100 симв): {r.text[:100]}")
                self.enable_btn()
                return

            self.log(f"Токен отримано: {token[:10]}...")

            headers = {
                "__RequestVerificationToken": token,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": f"{HOST}/html/home.html"
            }

            # 2. Вимикаємо дані
            self.log("Вимикаємо мобільні дані...")
            xml_off = '<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>0</dataswitch></request>'
            try:
                resp_off = s.post(f"{HOST}/api/dialup/mobile-dataswitch", data=xml_off, headers=headers, timeout=5)
                self.log(f"Запит вимкнення: {resp_off.status_code}")
                # Часто API повертає XML, перевіримо його
                if "<response>OK</response>" in resp_off.text:
                    self.log("Успішно вимкнено.")
                else:
                    self.log(f"Відповідь модема: {resp_off.text}")
            except Exception as e:
                self.log(f"Помилка при вимкненні: {e}")

            # Чекаємо
            self.log("Чекаємо 2 секунди...")
            time.sleep(2)

            # 3. Вмикаємо дані
            self.log("Вмикаємо мобільні дані...")
            xml_on = '<?xml version="1.0" encoding="UTF-8"?><request><dataswitch>1</dataswitch></request>'
            try:
                resp_on = s.post(f"{HOST}/api/dialup/mobile-dataswitch", data=xml_on, headers=headers, timeout=5)
                self.log(f"Запит ввімкнення: {resp_on.status_code}")
                if "<response>OK</response>" in resp_on.text:
                    self.log("Успішно ввімкнено.")
                else:
                    self.log(f"Відповідь модема: {resp_on.text}")
            except Exception as e:
                self.log(f"Помилка при ввімкненні: {e}")

            self.log("Готово!")

        except Exception as e:
            self.log(f"Критична помилка: {str(e)}")
            traceback.print_exc()
        finally:
            self.enable_btn()

    def enable_btn(self):
        Clock.schedule_once(lambda dt: setattr(self.btn, 'disabled', False))

if __name__ == "__main__":
    ModemRebooterApp().run()
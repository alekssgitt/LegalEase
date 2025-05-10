import flet as ft
import httpx
import logging
from typing import Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LegalEaseUI:
    def __init__(self):
        self.selected_file: Optional[str] = None
        self.api_url = "http://localhost:8000"
        self.page = None

        self.qa_file: Optional[str] = None
        self.qa_response_area = None
        self.qa_question_box = None
        
    def main(self, page: ft.Page):
        self.page = page
        
        page.title = "LegalEase"
        page.theme_mode = ft.ThemeMode.SYSTEM
        page.window_width = 800
        page.window_height = 800
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        
        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Document Analysis", content=self._build_analysis_tab()),
                ft.Tab(text="Legal Q&A", content=self._build_qa_tab()),
            ]
        )
        page.add(tabs)

    def _build_analysis_tab(self):
        self.file_picker = ft.FilePicker(
            on_result=self.on_file_picked
        )
        self.page.overlay.append(self.file_picker)
        
        self.profile_dropdown = ft.Dropdown(
            label="User Profile",
            hint_text="Select your profile",
            options=[
                ft.dropdown.Option("student", "Student"),
                ft.dropdown.Option("business_owner", "Business Owner"),
                ft.dropdown.Option("tenant", "Tenant"),
                ft.dropdown.Option("lawyer", "Lawyer"),
            ],
            width=200,
        )
        
        self.experience_dropdown = ft.Dropdown(
            label="Experience Level",
            hint_text="Select your experience level",
            options=[
                ft.dropdown.Option("beginner", "Beginner"),
                ft.dropdown.Option("intermediate", "Intermediate"),
                ft.dropdown.Option("advanced", "Advanced"),
                ft.dropdown.Option("expert", "Expert"),
            ],
            width=200,
            value="beginner"
        )
        
        self.selected_file_text = ft.Text("No file selected", size=12, color=ft.Colors.GREY_500)
        
        self.response_area = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            height=400,
            width=700,
            controls=[]
        )
        
        return ft.Column([
            ft.Text("LegalEase", size=32, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Upload your legal document and get an AI-powered analysis",
                size=18,
                color=ft.Colors.GREY_700
            ),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(
                    "Choose File",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda _: self.file_picker.pick_files(
                        allowed_extensions=["pdf", "txt"]
                    )
                ),
                self.selected_file_text,
            ]),
            ft.Row([
                self.profile_dropdown,
                self.experience_dropdown,
                ft.ElevatedButton(
                    "Analyze",
                    icon=ft.Icons.SEND,
                    on_click=self.analyze_document,
                    disabled=False
                ),
            ]),
            ft.Container(
                content=self.response_area,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=10,
                padding=10,
                height=400,
            ),
        ])
    
    def _build_qa_tab(self):
        self.qa_question_box = ft.TextField(label="Ask a legal question", multiline=True, width=400)
        self.qa_response_area = ft.Column([])
        qa_file_picker = ft.FilePicker(on_result=self._on_qa_file_picked)
        upload_btn = ft.ElevatedButton("Upload File for Q&A", on_click=lambda _: qa_file_picker.pick_files())
        ask_btn = ft.ElevatedButton("Ask", on_click=self._on_qa_ask)
        return ft.Column([
            self.qa_question_box,
            ft.Row([upload_btn, ask_btn]),
            self.qa_response_area,
            qa_file_picker
        ])

    def on_file_picked(self, e):
        if e.files:
            self.selected_file = e.files[0]
            self.selected_file_text.value = f"Selected: {self.selected_file.name}"
        else:
            self.selected_file = None
            self.selected_file_text.value = "No file selected"
        self.selected_file_text.update()
    
    def add_response_message(self, text: str, is_error: bool = False):
        self.response_area.controls.append(
            ft.Container(
                content=ft.Text(text, size=14, color=ft.Colors.BLACK),
                bgcolor=ft.Colors.RED_100 if is_error else ft.Colors.BLUE_50,
                padding=10,
                border_radius=10,
                width=600,
            )
        )
        self.response_area.update()
    
    def analyze_document(self, e):
        if not self.selected_file or not self.profile_dropdown.value:
            self.add_response_message("Please select a file and profile type first.", is_error=True)
            return
        
        try:
            files = {
                'file': (
                    self.selected_file.name,
                    open(self.selected_file.path, 'rb'),
                    'application/pdf' if self.selected_file.name.endswith('.pdf') else 'text/plain'
                )
            }
            data = {
                'profile_type': self.profile_dropdown.value,
                'experience_level': self.experience_dropdown.value
            }
            
            response = httpx.post(
                f"{self.api_url}/analyze",
                files=files,
                data=data,
                timeout=300.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("summary"):
                    self.add_response_message("Summary:\n" + result["summary"])
                
                if result.get("key_points"):
                    points = "\n".join(f"• {point}" for point in result["key_points"])
                    self.add_response_message("Key Points:\n" + points)
                
                if result.get("risks"):
                    risks = "\n".join(f"• {risk}" for risk in result["risks"])
                    self.add_response_message("Risks:\n" + risks)
                
                if result.get("recommendations"):
                    recs = "\n".join(f"• {rec}" for rec in result["recommendations"])
                    self.add_response_message("Recommendations:\n" + recs)
                
            else:
                self.add_response_message(
                    f"Error: {response.json().get('detail', 'Unknown error')}",
                    is_error=True
                )
                
        except httpx.ReadTimeout:
            self.add_response_message(
                "Request timed out after 5 minutes. The analysis is taking longer than expected.",
                is_error=True
            )
        except Exception as ex:
            self.add_response_message(f"Error: {str(ex)}", is_error=True)

    def _on_qa_file_picked(self, e):
        if e.files:
            self.qa_file = e.files[0]
            self.qa_response_area.controls.append(ft.Text(f"Selected Q&A file: {self.qa_file.name}", color=ft.Colors.BLUE))
            self.qa_response_area.update()
        else:
            self.qa_file = None

    def _on_qa_ask(self, e):
        question = self.qa_question_box.value
        if not question:
            self.qa_response_area.controls.append(ft.Text("Please enter a question.", color=ft.Colors.RED))
            self.qa_response_area.update()
            return
        files = None
        if self.qa_file:
            files = {"file": (self.qa_file.name, open(self.qa_file.path, "rb"), "application/pdf" if self.qa_file.name.endswith(".pdf") else "text/plain")}
        data = {"question": question}
        try:
            response = httpx.post(f"{self.api_url}/legal-qa", data=data, files=files, timeout=120.0)
            if response.status_code == 200:
                answer = response.json()["answer"]
                self.qa_response_area.controls.append(ft.Text(f"Answer: {answer}", color=ft.Colors.GREEN))
            else:
                self.qa_response_area.controls.append(ft.Text(f"Error: {response.text}", color=ft.Colors.RED))
            self.qa_response_area.update()
        except Exception as ex:
            self.qa_response_area.controls.append(ft.Text(f"Error: {str(ex)}", color=ft.Colors.RED))
            self.qa_response_area.update()

def main(page: ft.Page):
    app = LegalEaseUI()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)

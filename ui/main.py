import flet as ft
import httpx
import logging
import argparse
import os
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
        

        self.primary_color = "#1565C0"
        self.secondary_color = "#E3F2FD"
        self.accent_color = "#64B5F6"
        self.background_color = "#FFFFFF"
        self.text_color = "#212121"
        self.error_color = "#FFC107"
        
    def main(self, page: ft.Page):
        self.page = page
        
        page.title = "LegalEase"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1000
        page.window_height = 800
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        page.bgcolor = self.background_color
        
        header = ft.Container(
            content=ft.Column([
                ft.Text("LegalEase", size=40, weight=ft.FontWeight.BOLD, color=self.primary_color),
                ft.Text(
                    "AI-powered legal document analysis and Q&A",
                    size=16,
                    color=self.text_color,
                    italic=True
                ),
            ]),
            padding=ft.padding.only(bottom=10),
        )
        
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Document Analysis", content=self._build_analysis_tab()),
                ft.Tab(text="Legal Q&A", content=self._build_qa_tab()),
            ]
        )
        
        footer = ft.Container(
            content=ft.Text(" 2025 LegalEase - AI Legal Assistant", 
                           size=12, 
                           color="#757575",  # Grey 600
                           text_align=ft.TextAlign.CENTER),
            padding=10,
            alignment=ft.alignment.center
        )
        
        page.add(header, tabs, footer)

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
            border_color=self.primary_color,
            focused_border_color=self.accent_color,
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
            value="beginner",
            border_color=self.primary_color,
            focused_border_color=self.accent_color,
        )
        
        self.selected_file_text = ft.Text("No file selected", size=14, color="#9E9E9E")  # Grey 500
        
        self.response_area = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            height=400,
            width=900,
            controls=[]
        )
        
        clear_button = ft.ElevatedButton(
            "Clear Results",
            on_click=self._clear_analysis_results,
            style=ft.ButtonStyle(
                color="#FFFFFF",
                bgcolor="#FFC107",
            )
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(
                        "Upload your legal document and get an AI-powered analysis",
                        size=18,
                        color=self.text_color
                    ),
                    padding=ft.padding.only(bottom=10),
                ),
                ft.Divider(height=1, color="#BDBDBD"),  # Grey 300
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "Choose File",
                            on_click=lambda _: self.file_picker.pick_files(
                                allowed_extensions=["pdf", "txt"]
                            ),
                            style=ft.ButtonStyle(
                                color="#FFFFFF",  # White
                                bgcolor=self.primary_color,
                            )
                        ),
                        self.selected_file_text,
                    ]),
                    padding=ft.padding.only(top=10, bottom=10),
                ),
                ft.Container(
                    content=ft.Row([
                        self.profile_dropdown,
                        ft.Container(width=10),  # Spacer
                        self.experience_dropdown,
                        ft.Container(width=10),  # Spacer
                        ft.ElevatedButton(
                            "Analyze",
                            on_click=self.analyze_document,
                            style=ft.ButtonStyle(
                                color="#FFFFFF",  # White
                                bgcolor=self.accent_color,
                            )
                        ),
                        ft.Container(width=10),  # Spacer
                        clear_button,
                    ]),
                    padding=ft.padding.only(bottom=10),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Analysis Results", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.response_area,
                            border=ft.border.all(1, "#BDBDBD"),  # Grey 300
                            border_radius=10,
                            padding=15,
                            bgcolor=self.secondary_color,
                            height=400,
                        ),
                    ]),
                ),
            ]),
            padding=10,
        )
    
    def _build_qa_tab(self):
        self.qa_question_box = ft.TextField(
            label="Ask a legal question", 
            multiline=True, 
            min_lines=3,
            max_lines=5,
            width=800,
            border_color=self.primary_color,
            focused_border_color=self.accent_color,
        )
        
        self.qa_response_area = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            height=400,
        )
        
        qa_file_picker = ft.FilePicker(on_result=self._on_qa_file_picked)
        self.page.overlay.append(qa_file_picker)
        
        upload_btn = ft.ElevatedButton(
            "Upload Document", 
            on_click=lambda _: qa_file_picker.pick_files(allowed_extensions=["pdf", "txt"]),
            style=ft.ButtonStyle(
                color="#FFFFFF",  # White
                bgcolor=self.primary_color,
            )
        )
        
        ask_btn = ft.ElevatedButton(
            "Ask Question", 
            on_click=self._on_qa_ask,
            style=ft.ButtonStyle(
                color="#FFFFFF",  # White
                bgcolor=self.accent_color,
            )
        )
        
        # Clear button for Q&A tab
        clear_qa_btn = ft.ElevatedButton(
            "Clear Chat",
            on_click=self._clear_qa_results,
            style=ft.ButtonStyle(
                color="#FFFFFF",  # White
                bgcolor="#FFC107",  # Red 400
            )
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(
                        "Ask legal questions about uploaded documents or general legal inquiries",
                        size=18,
                        color=self.text_color
                    ),
                    padding=ft.padding.only(bottom=10),
                ),
                ft.Divider(height=1, color="#BDBDBD"),  # Grey 300
                ft.Container(
                    content=self.qa_question_box,
                    padding=ft.padding.only(top=10, bottom=10),
                ),
                ft.Container(
                    content=ft.Row([
                        upload_btn,
                        ft.Container(width=10),  # Spacer
                        ask_btn,
                        ft.Container(width=10),  # Spacer
                        clear_qa_btn,
                    ]),
                    padding=ft.padding.only(bottom=10),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Conversation", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.qa_response_area,
                            border=ft.border.all(1, "#BDBDBD"),  # Grey 300
                            border_radius=10,
                            padding=15,
                            bgcolor=self.secondary_color,
                            height=400,
                        ),
                    ]),
                ),
            ]),
            padding=10,
        )

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
                content=ft.Text(text, size=14, color="#000000"),  # Black
                bgcolor=self.error_color if is_error else self.secondary_color,
                padding=15,
                border_radius=10,
                width=850,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color="#000000",  # Black
                    offset=ft.Offset(0, 2)
                )
            )
        )
        self.response_area.update()
    
    def _clear_analysis_results(self, e):
        self.response_area.controls.clear()
        self.response_area.update()
    
    def _clear_qa_results(self, e):
        self.qa_response_area.controls.clear()
        self.qa_response_area.update()
        self.qa_question_box.value = ""
        self.qa_question_box.update()
    
    def analyze_document(self, e):
        if not self.selected_file or not self.profile_dropdown.value:
            self.add_response_message("Please select a file and profile type first.", is_error=True)
            return
        
        try:
            loading_msg = ft.Container(
                content=ft.Row([
                    ft.ProgressRing(width=16, height=16, stroke_width=2),
                    ft.Text("  Analyzing document...", size=14)
                ]),
                padding=10
            )
            self.response_area.controls.append(loading_msg)
            self.response_area.update()
            
            with open(self.selected_file.path, 'rb') as file_content:
                file_bytes = file_content.read()
            
            files = {
                'file': (
                    self.selected_file.name,
                    file_bytes,
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
            
            self.response_area.controls.remove(loading_msg)
            self.response_area.update()
            
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
            self.qa_response_area.controls.append(
                ft.Container(
                    content=ft.Text(f"Selected document: {self.qa_file.name}", size=14),
                    bgcolor=self.secondary_color,
                    padding=10,
                    border_radius=8,
                )
            )
            self.qa_response_area.update()
        else:
            self.qa_file = None

    def _on_qa_ask(self, e):
        if not self.qa_question_box.value:
            self.qa_response_area.controls.append(
                ft.Container(
                    content=ft.Text("Please enter a question", size=14, color="#FF0000"),
                    padding=10,
                )
            )
            self.qa_response_area.update()
            return
        
        question = self.qa_question_box.value
        self.qa_response_area.controls.append(
            ft.Container(
                content=ft.Text(f"You: {question}", size=14),
                bgcolor="#F7F7F7",  # Grey 200
                padding=15,
                border_radius=10,
                width=700,
            )
        )
        
        loading = ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=16, height=16, stroke_width=2),
                ft.Text("  Thinking...", size=14)
            ]),
            padding=10
        )
        self.qa_response_area.controls.append(loading)
        self.qa_response_area.update()
        
        try:
            data = {'question': question}
            files = {}
            
            if self.qa_file:
                with open(self.qa_file.path, 'rb') as file_content:
                    file_bytes = file_content.read()
                
                files['file'] = (
                    self.qa_file.name,
                    file_bytes,
                    'application/pdf' if self.qa_file.name.endswith('.pdf') else 'text/plain'
                )
            
            response = httpx.post(
                f"{self.api_url}/legal_qa",
                data=data,
                files=files,
                timeout=300.0
            )
            
            self.qa_response_area.controls.remove(loading)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "Sorry, I couldn't generate an answer.")
                
                self.qa_response_area.controls.append(
                    ft.Container(
                        content=ft.Text(f"LegalEase: {answer}", size=14),
                        bgcolor=self.secondary_color,
                        padding=15,
                        border_radius=10,
                        width=700,
                        margin=ft.margin.only(left=50),
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=4,
                            color="#000000",  # Black
                            offset=ft.Offset(0, 2)
                        )
                    )
                )
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                self.qa_response_area.controls.append(
                    ft.Container(
                        content=ft.Text(f"Error: {error_msg}", size=14, color="#FF0000"),
                        padding=10,
                    )
                )
        except Exception as ex:
            if loading in self.qa_response_area.controls:
                self.qa_response_area.controls.remove(loading)
            
            self.qa_response_area.controls.append(
                ft.Container(
                    content=ft.Text(f"Error: {str(ex)}", size=14, color="#FF0000"),
                    padding=10,
                )
            )
        
        self.qa_response_area.update()
        
        self.qa_question_box.value = ""
        self.qa_question_box.update()

def main(page: ft.Page):
    ui = LegalEaseUI()
    ui.main(page)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LegalEase UI')
    parser.add_argument('--port', type=int, default=8550, help='Port to run the UI on')
    args = parser.parse_args()
    
    ft.app(target=main, port=args.port)

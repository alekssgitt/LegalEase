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
        self.qa_selected_file_text = ft.Text("No document for Q&A context.")
        

        self.primary_color = "#1565C0"
        self.secondary_color = "#E3F2FD"
        self.accent_color = "#64B5F6"
        self.background_color = "#FFFFFF"
        self.text_color = "#212121"
        self.error_color = "#FFC107"
        
    def initializePage(self, page: ft.Page):
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
                ft.Tab(text="Document Analysis", content=self.buildAnalysisTab()),
                ft.Tab(text="Legal Q&A", content=self.buildQaTab()),
            ]
        )
        
        footer = ft.Container(
            content=ft.Text(" 2025 LegalEase - AI Legal Assistant", 
                           size=12, 
                           color="#757575",
                           text_align=ft.TextAlign.CENTER),
            padding=10,
            alignment=ft.alignment.center
        )
        
        page.add(header, tabs, footer)

    def buildAnalysisTab(self):
        self.file_picker = ft.FilePicker(
            on_result=self.onFilePicked
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
            on_click=self.clearAnalysisResults,
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
                ft.Divider(height=1, color="#BDBDBD"),
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "Choose File",
                            on_click=lambda _: self.file_picker.pick_files(
                                allowed_extensions=["pdf", "txt"]
                            ),
                            style=ft.ButtonStyle(
                                color="#FFFFFF",
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
                        ft.Container(width=10),
                        self.experience_dropdown,
                        ft.Container(width=10),
                        ft.ElevatedButton(
                            "Analyze",
                            on_click=self.analyzeDocument,
                            style=ft.ButtonStyle(
                                color="#FFFFFF",
                                bgcolor=self.accent_color,
                            )
                        ),
                        ft.Container(width=10),
                        clear_button,
                    ]),
                    padding=ft.padding.only(bottom=10),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Analysis Results", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.response_area,
                            border=ft.border.all(1, "#BDBDBD"),
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
    
    def buildQaTab(self):
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
        
        qa_file_picker = ft.FilePicker(on_result=self.onQaFilePicked)
        self.page.overlay.append(qa_file_picker)
        
        upload_btn = ft.ElevatedButton(
            "Upload Context Doc", 
            on_click=lambda _: qa_file_picker.pick_files(allowed_extensions=["pdf", "txt"]),
            style=ft.ButtonStyle(
                color="#FFFFFF",
                bgcolor=self.primary_color,
            )
        )

        clear_context_doc_btn = ft.ElevatedButton(
            "Clear Context Doc",
            on_click=self.clearQaDocumentContext,
            style=ft.ButtonStyle(
                color="#FFFFFF",
                bgcolor=self.error_color,
            )
        )
        
        ask_btn = ft.ElevatedButton(
            "Ask Question", 
            on_click=self.onQaAsk,
            style=ft.ButtonStyle(
                color="#FFFFFF",
                bgcolor=self.accent_color,
            )
        )
        

        clear_qa_btn = ft.ElevatedButton(
            "Clear Chat",
            on_click=self.clearQaResults,
            style=ft.ButtonStyle(
                color="#FFFFFF",
                bgcolor="#FFC107",
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
                ft.Divider(height=1, color="#BDBDBD"),
                ft.Container(
                    content=self.qa_question_box,
                    padding=ft.padding.only(top=10, bottom=10),
                ),
                ft.Container(
                    content=ft.Row([
                        upload_btn,
                        ft.Container(width=10),
                        clear_context_doc_btn,
                        ft.Container(width=10),
                        ask_btn,
                        ft.Container(width=10),
                        clear_qa_btn,
                    ]),
                    padding=ft.padding.only(bottom=5),
                ),
                ft.Container(
                    content=self.qa_selected_file_text,
                    padding=ft.padding.only(bottom=10)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Conversation", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.qa_response_area,
                            border=ft.border.all(1, "#BDBDBD"),
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

    def onFilePicked(self, e):
        if e.files:
            self.selected_file = e.files[0]
            self.selected_file_text.value = f"Selected: {self.selected_file.name}"
        else:
            self.selected_file = None
            self.selected_file_text.value = "No file selected"
        self.selected_file_text.update()
    
    def addResponseMessage(self, text: str, is_error: bool = False):
        self.response_area.controls.append(
            ft.Container(
                content=ft.Text(text, size=14, color="#000000"),
                bgcolor=self.error_color if is_error else self.secondary_color,
                padding=15,
                border_radius=10,
                width=850,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color="#000000",
                    offset=ft.Offset(0, 2)
                )
            )
        )
        self.response_area.update()
    
    def clearAnalysisResults(self, e):
        self.response_area.controls.clear()
        self.response_area.update()
    
    def clearQaResults(self, e):
        self.qa_response_area.controls.clear()
        self.qa_response_area.update()
        self.qa_question_box.value = ""
        self.qa_question_box.update()
    
    def analyzeDocument(self, e):
        if not self.selected_file or not self.profile_dropdown.value:
            self.addResponseMessage("Please select a file and profile type first.", is_error=True)
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
                'experience_level': self.experience_dropdown.value,
                'question': 'Analyze this document.'
            }
            
            response = httpx.post(
                f"{self.api_url}/process_input",
                files=files,
                data=data,
                timeout=1000
            )
            
            self.response_area.controls.remove(loading_msg)
            self.response_area.update()
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("summary"):
                    self.addResponseMessage("Summary:\n" + result["summary"])
                
                if result.get("key_points"):
                    points = "\n".join(f"• {point}" for point in result["key_points"])
                    self.addResponseMessage("Key Points:\n" + points)
                
                if result.get("risks"):
                    risks = "\n".join(f"• {risk}" for risk in result["risks"])
                    self.addResponseMessage("Risks:\n" + risks)
                
                if result.get("recommendations"):
                    recs = "\n".join(f"• {rec}" for rec in result["recommendations"])
                    self.addResponseMessage("Recommendations:\n" + recs)
                
            else:
                self.addResponseMessage(
                    f"Error: {response.json().get('detail', 'Unknown error')}",
                    is_error=True
                )
                
        except httpx.ReadTimeout:
            self.addResponseMessage(
                "Request timed out after 10 minutes. The analysis is taking longer than expected.",
                is_error=True
            )
        except Exception as ex:
            self.addResponseMessage(f"Error: {str(ex)}", is_error=True)

    def onQaFilePicked(self, e):
        if e.files:
            self.qa_file = e.files[0]
            self.qa_selected_file_text.value = f"Using context: {self.qa_file.name}"
        else:
            self.qa_file = None
            self.qa_selected_file_text.value = "No document for Q&A context."
        self.qa_selected_file_text.update()

    def clearQaDocumentContext(self, e):
        self.qa_file = None
        self.qa_selected_file_text.value = "No document for Q&A context."
        self.qa_selected_file_text.update()
        self.qa_response_area.controls.append(
            ft.Container(
                content=ft.Text("Document context cleared.", italic=True, color="#757575"),
                padding=5,
            )
        )
        self.qa_response_area.update()

    def onQaAsk(self, e):
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
                bgcolor="#F7F7F7",
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
            data = {
                'question': question,
                'profile_type': 'student',
                'experience_level': 'beginner'
            }
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
                f"{self.api_url}/process_input",
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
                            color="#000000",
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

def start_flet_app(page: ft.Page):
    ui = LegalEaseUI()
    ui.initializePage(page)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LegalEase UI')
    parser.add_argument('--port', type=int, default=8550)
    args = parser.parse_args()
    
    ft.app(target=start_flet_app, port=args.port)

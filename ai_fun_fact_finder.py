import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel, Label, Text, Button, ttk
from PIL import Image, ImageTk, ExifTags  # Import Pillow for handling images
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
import os

# Define the path for the blank icon and the image path
icon_path = 'C:\\Users\\Frank\\Desktop\\blank.ico'
image_path = 'C:\\Users\\Frank\\Desktop\\image.jpg'  # Path to your JPEG image

# Create a blank (transparent) ICO file if it doesn't exist
def create_blank_ico(path):
    size = (16, 16)  # Size of the icon
    image = Image.new("RGBA", size, (255, 255, 255, 0))  # Transparent image
    image.save(path, format="ICO")

# Create the blank ICO file
create_blank_ico(icon_path)

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = "Your API Key Here"

# Initialize the OpenAI model
llm = ChatOpenAI(model_name="gpt-4o-mini")

# Modify the prompt template to ensure dynamic math questions
prompt_template = PromptTemplate(
    input_variables=["topic"],
    template="""
    For the topic {topic}, please provide the following in this order:
    1. A concise, direct answer to the question: What is the deepest part of the ocean and how deep is it?
    2. A fun fact
    3. A joke that a child would enjoy
    4. A unique math question with random numbers related to the topic, suitable for a child, followed by the answer
    """
)

# Create the LLM chain
chain1 = LLMChain(prompt=prompt_template, llm=llm)

# Function to format and insert text into the Text widget
def insert_formatted_text(text_widget, text, tag_name):
    text_widget.insert(tk.END, text + "\n\n", tag_name)

# Function to get response from OpenAI and display it in a new window
def get_response_and_display():
    user_topic = topic_entry.get().strip()  # Get the entered topic (e.g., animals)
    
    if user_topic:  # Only proceed if a topic is entered
        status_label.config(text="Please wait...")
        root.update_idletasks()
        try:
            # Pass the topic into the LLM chain
            response = chain1({
                "topic": user_topic
            })
            content = response["text"]
            status_label.config(text="Response received, displaying...")
            root.update_idletasks()

            # Remove extra lines like ### 2. A, ### 3. A, etc.
            content = content.replace('### 2. A', '').replace('### 3. A', '').replace('### 4. A', '')
            
            # Remove any mention of "8-year-old"
            content = content.replace('An 8-year-old might want to know', 'Answer:')

            # Create a new window for displaying the response
            response_window = Toplevel(root)
            response_window.title("Response")
            response_window.geometry("600x400")
            response_window.iconbitmap(icon_path)

            # Create the Text widget for displaying formatted text
            response_text = Text(response_window, wrap=tk.WORD, font=("Arial", 12))
            response_text.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
            
            # Add color tags for different sections
            response_text.tag_config("title", font=("Comic Sans MS", 14, "bold"), foreground="blue")
            response_text.tag_config("answer", foreground="darkblue", font=("Arial", 12, "bold"))
            response_text.tag_config("fact", foreground="green", font=("Arial", 12, "italic"))
            response_text.tag_config("joke", foreground="purple", font=("Arial", 12))
            response_text.tag_config("math", foreground="orange", font=("Arial", 12, "bold"))

            # Split the response content based on keywords (handling different possible formats)
            answer = ""
            fun_fact = ""
            joke = ""
            math_question = ""

            if "Fun Fact:" in content:
                parts = content.split("Fun Fact:")
                answer = parts[0].strip()
                if "Joke:" in parts[1]:
                    fact_joke_math = parts[1].split("Joke:")
                    fun_fact = fact_joke_math[0].strip()
                    if "Math" in fact_joke_math[1]:
                        joke, math_question = fact_joke_math[1].split("Math")
                        joke = joke.strip()
                        math_question = "Math" + math_question.strip()
                    else:
                        joke = fact_joke_math[1].strip()
                else:
                    fun_fact = parts[1].strip()

            # Insert the content with formatting
            insert_formatted_text(response_text, "Answer to Your Question:", "title")
            insert_formatted_text(response_text, answer, "answer")
            
            insert_formatted_text(response_text, "Fun Fact:", "title")
            insert_formatted_text(response_text, fun_fact, "fact")
            
            if joke:
                insert_formatted_text(response_text, "Joke:", "title")
                insert_formatted_text(response_text, joke, "joke")
            
            if math_question:
                insert_formatted_text(response_text, "Math Question:", "title")
                insert_formatted_text(response_text, math_question, "math")

            # Disable the text widget to make it read-only
            response_text.config(state=tk.DISABLED)
            
            status_label.config(text="Response displayed")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            status_label.config(text="Error")
    else:
        messagebox.showwarning("Input Error", "Please enter a topic.")
        status_label.config(text="")

# Setting up the GUI for the child-friendly app
root = tk.Tk()
root.title("Fun Fact Finder")

# Set the window icon
root.iconbitmap(icon_path)

# Load and display the image with correct orientation
try:
    img = Image.open(image_path)
    
    # Check for EXIF orientation tag and correct orientation if necessary
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break
    try:
        exif = dict(img._getexif().items())
        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass
    
    img = img.resize((200, 200), Image.Resampling.LANCZOS)  # Use LANCZOS for resampling
    photo = ImageTk.PhotoImage(img)

    image_label = Label(root, image=photo)
    image_label.pack(pady=10)
except Exception as e:
    messagebox.showerror("Image Error", f"An error occurred while loading the image: {e}")

# Topic Entry
topic_label = tk.Label(root, text="Hi, what would you like to ask ?")
topic_label.pack(pady=5)
topic_entry = tk.Entry(root, width=50)
topic_entry.pack(pady=5)

# Status label
status_label = tk.Label(root, text="", fg="blue")
status_label.pack(pady=5)

# Frame to hold the buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# Submit button
submit_button = tk.Button(button_frame, text="Send", command=get_response_and_display, bg='#d0e8f1')
submit_button.pack(side=tk.LEFT, padx=10)

# Start the GUI event loop
root.mainloop()

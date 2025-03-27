import ollama
from PIL import Image
import base64
import io
from flask import Flask, request, render_template, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'sk-qwuiorh234089ef'  # 添加一个密钥用于session
app.config['SESSION_TYPE'] = 'filesystem'  # 使用文件系统存储session

def extract_text_from_image(image_bytes):
    """Extracts text from an image using Gemma-3 Vision."""
    try:
        response = ollama.chat(
            model='gemma3:12b',
            messages=[{
                'role': 'user',
                'content': """Analyze the text in the provided image. Extract all readable content
                            and present it in a structured Markdown format that is clear, concise, 
                            and well-organized. Ensure proper formatting (e.g., headings, lists, or
                            code blocks) as necessary to represent the content effectively.""",
                'images': [image_bytes]
            }]
        )
        
        return response.message.content
    except Exception as e:
        print(f"Error in extract_text_from_image: {str(e)}")
        return f"Error processing image: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                return render_template('index.html', error="请选择要上传的图片")
            
            file = request.files['image']
            if file.filename == '':
                return render_template('index.html', error="请选择要上传的图片")
            
            # 读取图片数据
            image_bytes = file.read()
            
            # 将图片转换为base64字符串
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # 提取文字
            extracted_text = extract_text_from_image(image_bytes)
            
            # 将数据存储在session中
            session['image_data'] = f"data:image/jpeg;base64,{image_base64}"
            session['extracted_text'] = extracted_text
            session.modified = True  # 确保session被修改
            
            print("Session data set successfully")
            print(f"Session contents: {session}")
            
            # 直接返回结果页面而不是重定向
            return render_template('result.html', 
                                 image_data=session['image_data'],
                                 extracted_text=session['extracted_text'])
            
        except Exception as e:
            print(f"Error in index route: {str(e)}")
            return render_template('index.html', error=f"处理图片时出错: {str(e)}")
    
    return render_template('index.html')

@app.route('/result')
def result():
    try:
        # 从session中获取数据
        image_data = session.get('image_data')
        extracted_text = session.get('extracted_text')
        
        print(f"Session data in result route: image_data={bool(image_data)}, extracted_text={bool(extracted_text)}")
        print(f"Full session contents: {session}")
        
        if not image_data or not extracted_text:
            print("Missing session data, redirecting to index")
            return redirect(url_for('index'))
        
        return render_template('result.html', 
                             image_data=image_data,
                             extracted_text=extracted_text)
    except Exception as e:
        print(f"Error in result route: {str(e)}")
        return render_template('index.html', error=f"显示结果时出错: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)

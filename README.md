<p>Sure! Here&#39;s a comprehensive README file for your GitHub project, including links to download the necessary tools:</p>
<hr>
<h1 id="phototransform">PhotoTransform</h1>
<p><strong>PhotoTransform</strong> is an advanced image processing tool that enhances and transforms photos using AI-powered upscaling and cropping. It automatically optimizes image quality and formats images to various aspect ratios, ideal for professional photographers, graphic designers, and digital content creators.</p>
<h2 id="features">Features</h2>
<ul>
<li><strong>AI Upscaling</strong>: Enhances image resolution and quality using Topaz Photo AI.</li>
<li><strong>Smart Cropping</strong>: Uses YOLOv5 to detect optimal crop coordinates.</li>
<li><strong>Format Conversion</strong>: Supports various aspect ratios including 4:3, 16:9, 1:1, 9:16, and 4:5.</li>
<li><strong>Automated Workflow</strong>: Integrates with RabbitMQ for efficient message handling and processing.</li>
</ul>
<h2 id="requirements">Requirements</h2>
<ul>
<li><a href="https://www.topazlabs.com/photo-ai">Topaz Photo AI</a> (for upscaling images)</li>
<li><a href="https://ffmpeg.org/download.html">FFmpeg</a> (for cropping and processing images)</li>
<li><a href="https://github.com/ultralytics/yolov5">YOLOv5</a> (for object detection)</li>
<li><a href="https://www.rabbitmq.com/download.html">RabbitMQ</a> (for message queuing)</li>
<li><a href="https://www.python.org/downloads/">Python 3.8+</a></li>
<li>Required Python packages (see <code>requirements.txt</code>)</li>
</ul>
<h2 id="installation">Installation</h2>
<ol>
<li><p><strong>Clone the repository:</strong></p>
<pre><code class="language-sh">git clone https://github.com/yourusername/phototransform.git
cd phototransform
</code></pre>
</li>
<li><p><strong>Install the required Python packages:</strong></p>
<pre><code class="language-sh">pip install -r requirements.txt
</code></pre>
</li>
<li><p><strong>Download and install the following tools:</strong></p>
<ul>
<li><strong>Topaz Photo AI:</strong> <a href="https://www.topazlabs.com/photo-ai">Download here</a></li>
<li><strong>FFmpeg:</strong> <a href="https://ffmpeg.org/download.html">Download here</a></li>
<li><strong>YOLOv5:</strong> <a href="https://github.com/ultralytics/yolov5">Instructions here</a></li>
<li><strong>RabbitMQ:</strong> <a href="https://www.rabbitmq.com/download.html">Download here</a></li>
</ul>
</li>
<li><p><strong>Configure paths in the script:</strong>
Update the paths for <code>local_temp_folder</code>, <code>output_folder</code>, <code>ffmpeg_path</code>, <code>photo_ai_path</code>, <code>yolov5_model_path</code>, and <code>yolov5_repo_path</code> in <code>phototransform.py</code> according to your system.</p>
</li>
</ol>
<h2 id="usage">Usage</h2>
<ol>
<li><p><strong>Start RabbitMQ server:</strong>
Follow the <a href="https://www.rabbitmq.com/download.html">RabbitMQ installation guide</a> to start the server.</p>
</li>
<li><p><strong>Run the PhotoTransform script:</strong></p>
<pre><code class="language-sh">python phototransform.py
</code></pre>
</li>
<li><p><strong>Send a message to RabbitMQ:</strong>
PhotoTransform will listen for messages in the &#39;convert-image-format&#39; queue. Each message should contain the following JSON structure:</p>
<pre><code class="language-json">{
    &quot;asset&quot;: {&quot;id&quot;: &quot;unique_id&quot;, &quot;filename&quot;: &quot;image.jpg&quot;},
    &quot;formats&quot;: [&quot;4x3&quot;, &quot;16x9&quot;, &quot;1x1&quot;, &quot;9x16&quot;, &quot;4x5&quot;]
}
</code></pre>
</li>
</ol>
<h2 id="folder-structure">Folder Structure</h2>
<ul>
<li><code>phototransform.py</code>: Main script for the project.</li>
<li><code>requirements.txt</code>: List of required Python packages.</li>
</ul>
<h2 id="contributing">Contributing</h2>
<p>We welcome contributions! Please read our <a href="CONTRIBUTING.md">contributing guidelines</a> for more details.</p>
<h2 id="license">License</h2>
<p>This project is licensed under the MIT License. See the <a href="LICENSE">LICENSE</a> file for details.</p>
<hr>
<p>Feel free to customize the content according to your specific requirements and replace placeholders like <code>https://github.com/yourusername/phototransform.git</code> with your actual GitHub repository URL.</p>

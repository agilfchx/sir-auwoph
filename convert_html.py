import os
import glob
import html
import re

def load_template(template_path='template.html'):
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()

def convert_to_html(content):
    template = load_template()
    return template.replace('{{file_contents}}', content)

def generate_report():
    combined_content = ''
    results_directory = 'results'
    plugin_counter = 0
    report_generated = False 

    overview_content = '''
        <div class="plugin-overview-header">Plugin Overview</div>
        <div class="plugin-overview">
            <ul class="list-group">
                <li class="list-group-item">
                    <strong>Plugin Scanned:</strong> {plugin_counter}
                </li>
            </ul>
        </div>
    '''

    for plugin_folder in glob.glob(os.path.join(results_directory, '*')):
        plugin_slug = os.path.basename(plugin_folder)
        plugin_name = plugin_slug.replace('-', ' ').title()
        vuln_folder = os.path.join(plugin_folder, 'vuln')

        accordion_id = html.escape(plugin_slug)
        emoji_icon = '🔧'

        file_counter = 1

        combined_content += f'''
        <div class="accordion" id="{accordion_id}">
            <div class="card">
                <div class="card-header" id="heading-{accordion_id}">
                    <h5 class="mb-0">
                        <button class="btn btn-link" type="button" data-toggle="collapse" data-target="#collapse-{accordion_id}" aria-expanded="false" aria-controls="collapse-{accordion_id}">
                            <span class="icon">{emoji_icon}</span> {plugin_name}
                            <span class="accordion-icon down"><i class="fas fa-chevron-down"></i></span>
                        </button>
                    </h5>
                </div>

                <div id="collapse-{accordion_id}" class="collapse" aria-labelledby="heading-{accordion_id}" data-parent="#{accordion_id}">
                    <div class="card-body">
        '''

        for vulnerability_folder in glob.glob(os.path.join(vuln_folder, '*')):
            for txt_file in glob.glob(os.path.join(vulnerability_folder, '*.txt')):
                with open(txt_file, 'r', encoding='utf-8') as file:
                    content = file.read()

                formatted_content = '<pre class="code-block"><code>'
                prev_line_number = None

                lines = content.split('\n')

                for line in lines:
                    if line.startswith('[File]'):
                        match = re.search(r'\((.*?)\)', line)
                        file_path = match.group(1) if match else None
                        continue

                    if line.startswith('[') and ']' in line:
                        line_number_str = line.split(']')[0][1:].strip()
                        try:
                            line_number = int(line_number_str)
                        except ValueError:
                            continue

                        sanitized_line = html.escape(']'.join(line.split(']')[1:]).strip())

                        if prev_line_number is not None and line_number != prev_line_number + 1:
                            formatted_content += '<p class="ellipsis">...</p>'

                        formatted_content += f'<p><span class="line-number">{line_number}</span> {sanitized_line}</p>'
                        prev_line_number = line_number
                    else:
                        sanitized_line = html.escape(line.strip())
                        formatted_content += f'<p>{sanitized_line}</p>'

                formatted_content += '</code></pre>'
                file_name = os.path.basename(txt_file).replace('.txt', '.php')
                file_info = f'<div class="file-info"><span class="file-number">{file_counter}</span><i class="file-icon fas fa-file-code"></i><strong>File:</strong> {file_name} ({html.escape(file_path if file_path else os.path.basename(txt_file))})</div>'
                file_counter += 1

                combined_content += file_info + formatted_content

        combined_content += '''
                    </div>
                </div>
            </div>
        </div>
        '''
        
        plugin_counter += 1

    overview_content = overview_content.format(plugin_counter=plugin_counter)
    combined_content = overview_content + combined_content

    output_file = os.path.join(results_directory, 'output.html')

    with open(output_file, 'w', encoding='utf-8') as html_file:
        html_file.write(convert_to_html(combined_content))

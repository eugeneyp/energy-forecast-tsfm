import os

def fix_shebangs():
    bin_dir = '.venv/bin'
    if not os.path.exists(bin_dir):
        print(f"{bin_dir} does not exist.")
        return
        
    old_path = '/Users/epeng/code/personal/energy-forecast-model/.venv/bin/python3'
    new_path = f'#!{os.path.abspath(".venv/bin/python3")}\n'
    
    print(f"Targeting path correction to: {new_path.strip()}")
    
    for filename in os.listdir(bin_dir):
        filepath = os.path.join(bin_dir, filename)
        if os.path.isfile(filepath) and not os.path.islink(filepath):
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                
                # Check if it starts with the bad shebang
                if content.startswith(b'#!/Users/epeng/code/personal/energy-forecast-model/'):
                    # Find first line
                    lines = content.split(b'\n')
                    old_shebang = lines[0].decode('utf-8')
                    print(f"Fixing {filename}: {old_shebang}")
                    lines[0] = f'#!{os.path.abspath(".venv/bin/python3")}'.encode('utf-8')
                    new_content = b'\n'.join(lines)
                    
                    with open(filepath, 'wb') as f:
                        f.write(new_content)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == '__main__':
    fix_shebangs()

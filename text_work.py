import subprocess

def inflect_to_accusative(name):
    ruby_script = '''
    require 'petrovich'

    def inflect_to_accusative(name)
      Petrovich(firstname: name).accusative.to_s
    end

    input_name = $stdin.gets.chomp
    accusative_name = inflect_to_accusative(input_name)
    puts accusative_name
    '''

    proc = subprocess.Popen(
        ['ruby', '-e', ruby_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'  # Set the encoding explicitly
    )

    stdout, stderr = proc.communicate(input=name)

    if stderr:
        raise RuntimeError(f"Ruby script execution error:\n{stderr}")

    return stdout.strip()

def inflect_to_dative(name):
    ruby_script = '''
    require 'petrovich'

    def inflect_to_dative(name)
      Petrovich(firstname: name).dative.to_s
    end

    input_name = $stdin.gets.chomp
    accusative_name = inflect_to_accusative(input_name)
    puts accusative_name
    '''

    proc = subprocess.Popen(
        ['ruby', '-e', ruby_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'  # Set the encoding explicitly
    )

    stdout, stderr = proc.communicate(input=name)

    if stderr:
        raise RuntimeError(f"Ruby script execution error:\n{stderr}")

    return stdout.strip()

def detect_gender(name, word_in_male, word_in_female):
    ruby_script = '''
    require 'petrovich'

    def detect_gender(name)
      gender = Petrovich(firstname: name).gender
      gender == :male ? 0 : 1
    end

    input_name = $stdin.gets.chomp
    gender_code = detect_gender(input_name)
    puts gender_code
    '''

    proc = subprocess.Popen(
        ['ruby', '-e', ruby_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'  # Set the encoding explicitly
    )

    stdout, stderr = proc.communicate(input=name)

    if stderr:
        raise RuntimeError(f"Ruby script execution error:\n{stderr}")
    if int(stdout.strip()):
        return word_in_female
    else:
        return word_in_male

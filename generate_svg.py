import subprocess


def eps2dxf(input_eps, output_dxf):
    """
    Uses the 

    :param input_eps:
    :param output_dxf:
    :return:
    """
    work_directory = "C:\Program Files\pstoedit"

    input_file = input_eps.split(".")[0]
    cmdline = "pstoedit -f dxf_s " + input_eps + " " + output_dxf
    subprocess.check_call(cmdline, cwd=work_directory, shell=True)
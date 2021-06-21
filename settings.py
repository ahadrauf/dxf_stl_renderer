class NoSettings:
    pass


class LaserCutter:
    """
    Universal Laser Cutter line settings
    Documentation: https://www.saic.edu/sites/default/files/Universal%20Laser%20Cutters%20Guide.pdf
    """
    CUT = 0
    ENGRAVE = 1
    RASTER = 2

    COLOR = [[255, 0, 0], [255, 255, 255], [255, 255, 255]]  # RGB
    LINEWIDTH = [0.0254, 0.0254, 1]  # mm

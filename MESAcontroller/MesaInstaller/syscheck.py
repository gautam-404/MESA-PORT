import platform

import cpuinfo


def whichos():
    """Determine the OS type.

    Raises:
        OSError: If OS is not compatible.

    Returns:
        str: OS type. 
    """
    if "macOS" in platform.platform():
        manufacturer = cpuinfo.get_cpu_info().get('brand_raw')
        arch = 'Intel' if 'intel' in manufacturer.lower() else 'ARM'
        return f"macOS-{arch}"
    elif "Linux" in platform.platform():
        return "Linux"
    else:
        raise OSError(f"OS {platform.platform()} not compatible.")
        
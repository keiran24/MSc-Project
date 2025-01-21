import warnings
import bottleneck as bn
import numpy as np


def moving_process(data, nwindow, func, loc='right', min_count=None, min_pct=-1, axis=-1):
    """
    Apply a moving window function to an array.
    If function available in bottleneck, use bottleneck function, otherwise ?.
    Arguments:
    data -- array_like: Input array.
    nwindow -- int: number of elements in the window.
    func -- str: Function to apply to each window.
    loc -- str: Location of the window. Default is 'right'.
    min_count -- int: Minimum number of non-NaN elements in the window. (default None = nwindow)
    min_pct -- int [0;100]: Minimum percentage of non-NaN elements in the window. (default -1 = nwindow)
    axis -- int: Axis along which to apply the moving window.

    Example:
    arr: [nan nan nan 2.5 3.5 4.5 5.5 6.5 7.5 8.5]
    mean on 4-length window: [nan nan nan 2.5 3.5 4.5 5.5 6.5 7.5 8.5]
    centred: [nan nan 2.5 3.5 4.5 5.5 6.5 7.5 8.5 nan]
    left: [2.5 3.5 4.5 5.5 6.5 7.5 8.5 nan nan nan]
    """
    if min_pct != -1:
        min_count = nwindow * min_pct/100
    if isinstance(min_count,float):
        warnings.warn(f'min_count = {min_count} must be an integer. Value considered: {int(min_count)}.')
        min_count = int(min_count)

    bottleneck_func = {f.__name__.split('_')[1]:f for f in bn.get_functions('move')}
    if func in bottleneck_func.keys():
        out = bottleneck_func[func](data, nwindow, min_count=min_count,axis=axis)
    else:
        raise ValueError(f'Function {func} not available in bottleneck. Other cases to be implemented.')
    
    if loc == 'center':
        out = np.roll(out, -nwindow//2+1, axis=axis)
    elif loc == 'left':
        out = np.roll(out, -nwindow+1, axis=axis)

    return out
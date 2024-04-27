from math import sqrt, log, exp


__all__ = ("SH_converter", )

# todo: check all the docstrings


class SH_converter(object):
    """
    Convert between temperature and resistance given the
    Steinhart and Hart coefficients of a termistor.
    """
    __slots__ = ("A", "B", "C", "Tl", "Th", )

    def __init__(self, A, B, C, Tl=None, Th=None):
        """
        Create converter with `A`, `B` and `C` coefficients.
        `Tl` and `Th` are respectively the lower temperature and
        higher temperature from which the coefficients have been
        computed.

        To create a converter starting from pairs of temperatures
        and resistances use `SH_converter.from_points`.
        """
        self.Tl, self.Th = Tl, Th
        self.A, self.B, self.C = A, B, C

    @staticmethod
    def from_points(TR_points):
        """
        Create a `SH_converter` by computing coefficients from
        three evenly spaced temperature-resistance pairs.
        `TR_points` is a sequence of three temp/res pairs.

        See `SH_converter`.
        """
        (T1, R1), (T2, R2), (T3, R3) = TR_points

        Tk1, Tk2, Tk3 = map(
            lambda x: x + 273.15, (T1, T2, T3))

        L1, L2, L3 = log(R1), log(R2), log(R3)
        Y1, Y2, Y3 = 1 / Tk1, 1 / Tk2, 1 / Tk3

        G2 = (Y2 - Y1) / (L2 - L1)
        G3 = (Y3 - Y1) / (L3 - L1)

        C = ((G3 - G2) / (L3 - L2)) * (L1 + L2 + L3)**-1
        B = G2 - C * (L1**2 + L1 * L2 + L2**2)
        A = Y1 - (B + L1**2 * C) * L1

        return SH_converter(A, B, C, T1, T3, )

    def temperature(self, R):
        """
        Calculate the temperature (Celsius) given the resistance.
        """
        A, B, C = self.A, self.B, self.C
        lnR = log(R)
        T = 1 / (A + B * lnR + C * lnR**3) - 273.15

        return T

    def resistance(self, T):
        """
        Calculate the resistance given the temperature (Celsius).
        
        Raise `ValueError` or `TypeError` if the coefficients are unfit
        to find the value with this implementation.
        """
        Tk = T + 273.15

        A, B, C = self.A, self.B, self.C
        x = 1 / (2 * C) * (A - 1 / Tk)
        y = sqrt((B / (3 * C))**3 + x**2)
        R = exp((y - x)**(1/3) - (y + x)**(1/3))

        return R

    def _to_str_impl(self, compact=False, with_temps=True):
        """
        Stringify (kinda) implementation used by
        `__repr__`, `__str__` and `to_cstr`.
        """
        A, B, C, Tl, Th = self.A, self.B, self.C, self.Tl, self.Th

        if compact:
            ABC = f"1./{round(1/A)}, 1./{round(1/B)}, 1./{round(1/C)}"
        else:
            ABC = f"{A}, {B}, {C}"

        if with_temps and Tl is not None and Th is not None:
            return f"{ABC}, {Tl}, {Th}"

        return f"{ABC}"

    def to_cstr(self, compact=False, with_temps=True):
        """
        Return a string with the `A`, `B` and `C` coefficients and,
        if available, the temperatures from which they've been
        derived.

        Use `with_temp` to control whether the low/high temperature
        should be printed.

        Use `compact` to use a shorter representation for `ABC`
        values (i.e. print the inverse formula for each coefficient).
        While prettier in source there could be a slight precision
        loss.
        """
        s = self._to_str_impl(compact, with_temps)
        return f"{{{s}}}"

    def __repr__(self):
        """
        Tentatively print the converter to satisfy

            converter = eval(converter)

        Where equality means different objects but same functionality.
        """
        s = self._to_str_impl(compact=False, with_temps=True)
        return f"SH_converter({s})"

    def __str__(self):
        """
        Create a string representation of the object.
        """
        s = self._to_str_impl(compact=True, with_temps=True)
        return f"SH_converter[{s}]"

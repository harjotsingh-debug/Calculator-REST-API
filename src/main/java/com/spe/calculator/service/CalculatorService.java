package com.spe.calculator.service;

import java.math.BigDecimal;
import java.math.MathContext;

import org.springframework.stereotype.Service;

/**
 * Core arithmetic. BigDecimal avoids floating-point surprises such as 0.1 + 0.2 = 0.30000000000000004.
 */
@Service
public class CalculatorService {

    // 16 significant digits (same as a double), so non-terminating divisions like 1/3 have a cut-off.
    private static final MathContext PRECISION = MathContext.DECIMAL64;

    public BigDecimal add(BigDecimal a, BigDecimal b) {
        return normalize(a.add(b));
    }

    public BigDecimal subtract(BigDecimal a, BigDecimal b) {
        return normalize(a.subtract(b));
    }

    public BigDecimal multiply(BigDecimal a, BigDecimal b) {
        return normalize(a.multiply(b));
    }

    public BigDecimal divide(BigDecimal a, BigDecimal b) {
        if (b.signum() == 0) {
            throw new ArithmeticException("Division by zero is not allowed");
        }
        return normalize(a.divide(b, PRECISION));
    }

    /** Drops trailing zeros so 5.00 is returned as 5. */
    private BigDecimal normalize(BigDecimal value) {
        return value.signum() == 0 ? BigDecimal.ZERO : value.stripTrailingZeros();
    }
}

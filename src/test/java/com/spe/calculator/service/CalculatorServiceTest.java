package com.spe.calculator.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.math.BigDecimal;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class CalculatorServiceTest {

    private final CalculatorService calculator = new CalculatorService();

    private static BigDecimal n(String value) {
        return new BigDecimal(value);
    }

    @Test
    @DisplayName("add: 2 + 3 = 5")
    void addsIntegers() {
        assertEquals(n("5"), calculator.add(n("2"), n("3")));
    }

    @Test
    @DisplayName("add: 0.1 + 0.2 = 0.3 exactly")
    void addsDecimalsWithoutFloatingPointError() {
        assertEquals(n("0.3"), calculator.add(n("0.1"), n("0.2")));
    }

    @Test
    @DisplayName("add: negative numbers")
    void addsNegativeNumbers() {
        assertEquals(n("-7"), calculator.add(n("-4"), n("-3")));
    }

    @Test
    @DisplayName("subtract: 10 - 4 = 6")
    void subtracts() {
        assertEquals(n("6"), calculator.subtract(n("10"), n("4")));
    }

    @Test
    @DisplayName("subtract: result can be negative")
    void subtractsToNegative() {
        assertEquals(n("-1.5"), calculator.subtract(n("1"), n("2.5")));
    }

    @Test
    @DisplayName("multiply: 6 * 7 = 42")
    void multiplies() {
        assertEquals(n("42"), calculator.multiply(n("6"), n("7")));
    }

    @Test
    @DisplayName("multiply: by zero gives 0")
    void multipliesByZero() {
        assertEquals(BigDecimal.ZERO, calculator.multiply(n("123.45"), n("0")));
    }

    @Test
    @DisplayName("divide: 10 / 4 = 2.5")
    void divides() {
        assertEquals(n("2.5"), calculator.divide(n("10"), n("4")));
    }

    @Test
    @DisplayName("divide: non-terminating result is rounded to 16 significant digits")
    void dividesNonTerminating() {
        assertEquals(n("0.3333333333333333"), calculator.divide(n("1"), n("3")));
    }

    @Test
    @DisplayName("divide: by zero throws ArithmeticException")
    void divideByZeroThrows() {
        ArithmeticException ex = assertThrows(ArithmeticException.class,
                () -> calculator.divide(n("5"), n("0")));
        assertEquals("Division by zero is not allowed", ex.getMessage());
    }

    @Test
    @DisplayName("divide: by 0.0 also throws")
    void divideByDecimalZeroThrows() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(n("5"), n("0.0")));
    }
}

package com.spe.calculator.model;

import java.math.BigDecimal;

/** Successful result, e.g. {"operation":"add","a":2,"b":3,"result":5}. */
public record CalculationResponse(String operation, BigDecimal a, BigDecimal b, BigDecimal result) {
}

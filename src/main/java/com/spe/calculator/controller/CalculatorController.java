package com.spe.calculator.controller;

import java.math.BigDecimal;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.spe.calculator.model.CalculationResponse;
import com.spe.calculator.service.CalculatorService;

@RestController
@RequestMapping("/api/v1")
public class CalculatorController {

    private final CalculatorService calculatorService;

    public CalculatorController(CalculatorService calculatorService) {
        this.calculatorService = calculatorService;
    }

    @GetMapping("/add")
    public CalculationResponse add(@RequestParam BigDecimal a, @RequestParam BigDecimal b) {
        return new CalculationResponse("add", a, b, calculatorService.add(a, b));
    }

    @GetMapping("/subtract")
    public CalculationResponse subtract(@RequestParam BigDecimal a, @RequestParam BigDecimal b) {
        return new CalculationResponse("subtract", a, b, calculatorService.subtract(a, b));
    }

    @GetMapping("/multiply")
    public CalculationResponse multiply(@RequestParam BigDecimal a, @RequestParam BigDecimal b) {
        return new CalculationResponse("multiply", a, b, calculatorService.multiply(a, b));
    }

    @GetMapping("/divide")
    public CalculationResponse divide(@RequestParam BigDecimal a, @RequestParam BigDecimal b) {
        return new CalculationResponse("divide", a, b, calculatorService.divide(a, b));
    }
}

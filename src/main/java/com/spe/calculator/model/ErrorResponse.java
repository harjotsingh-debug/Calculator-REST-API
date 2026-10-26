package com.spe.calculator.model;

import java.time.Instant;

/** Structured error body returned with every 400 response. */
public record ErrorResponse(Instant timestamp, int status, String error, String message, String path) {
}

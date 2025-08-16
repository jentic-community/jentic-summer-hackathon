"""OpenAPI specification validation using jsonschema and openapi-spec-validator."""

from typing import Dict, Any, List
from openapi_spec_validator import validate_spec
from openapi_spec_validator.exceptions import OpenAPISpecValidatorError
from jsonschema import ValidationError as JsonSchemaValidationError

from core.exceptions import ValidationError


class SpecValidator:
    """Validator for OpenAPI specifications using standard validation libraries."""

    def __init__(self):
        self.validation_errors: List[str] = []

    def validate(self, raw_spec: Dict[str, Any]) -> bool:
        """Validate OpenAPI specification structure and content.

        Parameters
        ----------
        raw_spec : Dict[str, Any]
            Raw OpenAPI specification data to validate.

        Returns
        -------
        bool
            True if specification is valid.

        Raises
        ------
        ValidationError
            If specification validation fails with details.
        """
        self.validation_errors.clear()

        try:
            self._validate_basic_structure(raw_spec)
            self._validate_openapi_spec(raw_spec)

            if self.validation_errors:
                raise ValidationError(
                    f"Specification validation failed with {len(self.validation_errors)} errors",
                    self.validation_errors,
                )

            return True

        except OpenAPISpecValidatorError as e:
            raise ValidationError(f"OpenAPI validation failed: {e}")
        except Exception as e:
            raise ValidationError(f"Validation error: {e}")

    def _validate_basic_structure(self, raw_spec: Dict[str, Any]) -> None:
        """Validate basic OpenAPI specification structure.

        Parameters
        ----------
        raw_spec : Dict[str, Any]
            Raw specification to validate.
        """
        required_fields = ["openapi", "info", "paths"]

        for field in required_fields:
            if field not in raw_spec:
                self.validation_errors.append(f"Missing required field: {field}")

        if "info" in raw_spec:
            info = raw_spec["info"]
            if not isinstance(info, dict):
                self.validation_errors.append("'info' must be an object")
            else:
                if "title" not in info:
                    self.validation_errors.append("Missing required field: info.title")
                if "version" not in info:
                    self.validation_errors.append("Missing required field: info.version")

        if "paths" in raw_spec:
            paths = raw_spec["paths"]
            if not isinstance(paths, dict):
                self.validation_errors.append("'paths' must be an object")
            elif not paths:
                self.validation_errors.append("'paths' object cannot be empty")

        if "openapi" in raw_spec:
            version = str(raw_spec["openapi"])
            if not version.startswith(("3.0", "3.1")):
                self.validation_errors.append(f"Unsupported OpenAPI version: {version}")

    def _validate_openapi_spec(self, raw_spec: Dict[str, Any]) -> None:
        """Validate using openapi-spec-validator library.

        Parameters
        ----------
        raw_spec : Dict[str, Any]
            Raw specification to validate.
        """
        try:
            validate_spec(raw_spec)
        except OpenAPISpecValidatorError as e:
            self.validation_errors.append(f"OpenAPI validation: {e}")
        except JsonSchemaValidationError as e:
            self.validation_errors.append(f"JSON Schema validation: {e.message}")
        except Exception as e:
            self.validation_errors.append(f"Validation library error: {e}")

    def validate_operation(self, operation: Dict[str, Any], method: str, path: str) -> List[str]:
        """Validate individual operation structure.

        Parameters
        ----------
        operation : Dict[str, Any]
            Operation object to validate.
        method : str
            HTTP method for the operation.
        path : str
            API path for the operation.

        Returns
        -------
        List[str]
            List of validation errors for this operation.
        """
        errors = []

        if not isinstance(operation, dict):
            errors.append(f"{method.upper()} {path}: Operation must be an object")
            return errors

        if "responses" not in operation:
            errors.append(f"{method.upper()} {path}: Missing required 'responses' field")
        elif not isinstance(operation["responses"], dict):
            errors.append(f"{method.upper()} {path}: 'responses' must be an object")
        elif not operation["responses"]:
            errors.append(f"{method.upper()} {path}: 'responses' cannot be empty")

        if "parameters" in operation:
            if not isinstance(operation["parameters"], list):
                errors.append(f"{method.upper()} {path}: 'parameters' must be an array")
            else:
                for i, param in enumerate(operation["parameters"]):
                    param_errors = self._validate_parameter(param, f"{method.upper()} {path}", i)
                    errors.extend(param_errors)

        if "requestBody" in operation:
            if not isinstance(operation["requestBody"], dict):
                errors.append(f"{method.upper()} {path}: 'requestBody' must be an object")

        return errors

    def _validate_parameter(
        self, parameter: Dict[str, Any], operation_ref: str, index: int
    ) -> List[str]:
        """Validate parameter structure.

        Parameters
        ----------
        parameter : Dict[str, Any]
            Parameter object to validate.
        operation_ref : str
            Reference to the operation for error messages.
        index : int
            Parameter index for error messages.

        Returns
        -------
        List[str]
            List of validation errors for this parameter.
        """
        errors = []
        param_ref = f"{operation_ref} parameter[{index}]"

        if not isinstance(parameter, dict):
            errors.append(f"{param_ref}: Parameter must be an object")
            return errors

        required_fields = ["name", "in"]
        for field in required_fields:
            if field not in parameter:
                errors.append(f"{param_ref}: Missing required field '{field}'")

        if "in" in parameter:
            valid_locations = ["query", "header", "path", "cookie"]
            if parameter["in"] not in valid_locations:
                errors.append(f"{param_ref}: Invalid 'in' value: {parameter['in']}")

        if parameter.get("in") == "path" and not parameter.get("required", False):
            errors.append(f"{param_ref}: Path parameters must be required")

        return errors

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation results.

        Returns
        -------
        Dict[str, Any]
            Summary of validation results including error count and details.
        """
        return {
            "is_valid": len(self.validation_errors) == 0,
            "error_count": len(self.validation_errors),
            "errors": self.validation_errors.copy(),
        }

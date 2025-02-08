from pydantic import BaseModel, ValidationError, model_validator
from typing import Any, Optional


class AugmentedValue(BaseModel):
    data: Any
    metadata: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_metadata(cls, values):
        """Validate before Pydantic validation."""
        data = values.get("data")
        metadata = values.get("metadata")

        # Log metadata validation error with data context
        if metadata is not None and not isinstance(metadata, str):
            raise ValueError(
                "Validation Error: metadata must be a string. "
                f"Got {metadata} (type={type(metadata)}) with data={data}"
            )
        return values

    def set_metadata(self, metadata):
        self.metadata = metadata

    def __repr__(self):
        return f"<AugmentedValue: data={self.data}; metadata={self.metadata}>"

    def __str__(self):
        return self.__repr__()


class AugmentedValueFactory:
    @staticmethod
    def create(data, metadata=None):
        return AugmentedValue(data=data, metadata=metadata)


class dictx:
    def __init__(self, data: dict, metadata: dict = dict()):
        self._validate_arguments(data, metadata)
        self._set_attributes_iter(data, metadata)

    def __getitem__(self, key: str):
        return self.__dict__[key]

    def __setitem__(self, key: str, value: AugmentedValue):  # TODO: Review interface
        self._set_attribute(k, value)

    def _validate_arguments(self, data: dict, metadata: dict):
        for arg in [data, metadata]:
            if not isinstance(arg, dict):
                raise TypeError(
                    "`dictx` arguments must be of type `dict` " f"(got {type(arg)})"
                )

    def _set_attributes_iter(self, data: dict, metadata: dict):
        for k, v in data.items():
            meta_v = metadata.get(k, None)
            self._set_attribute_poly(k, v, meta_v)

    def _set_attribute_poly(self, k, v, meta_v):  # TODO: typing / dispatch_method?
        if isinstance(v, (str, int, float)):
            dictx._validate_metadata_value(meta_v)
            self._set_attribute(k, AugmentedValueFactory.create(v, meta_v))
        elif isinstance(v, dict):
            self._set_dict_attribute(k, v, meta_v)
        elif isinstance(v, list):
            if not len(v):
                self._set_attribute(k, AugmentedValueFactory.create(v, meta_v))
            for vv in v:
                if isinstance(vv, dict):
                    self._set_dict_attribute(k, vv, meta_v)
                else:
                    dictx._validate_metadata_value(meta_v)
                    self._set_attribute(k, AugmentedValueFactory.create(vv, meta_v))

    def _set_attribute(self, k: str, augmented_value: AugmentedValue):
        if not isinstance(augmented_value, AugmentedValue):
            raise TypeError("Attribute values must be of type `AugmentedValue`")
        setattr(self, k, augmented_value)

    def _set_dict_attribute(self, k, v, meta_v):  # TODO: typing
        if isinstance(meta_v, dict):
            # Metadata is passed to the creation of `dictx`
            self._set_attribute(k, AugmentedValueFactory.create(dictx(v, meta_v)))
        else:
            # Metadata is attached to the `AugmentedValue`
            dictx._validate_metadata_value(meta_v)
            self._set_attribute(k, AugmentedValueFactory.create(dictx(v), meta_v))

    @staticmethod
    def _validate_metadata_value(meta_v):
        if meta_v:
            if not isinstance(meta_v, str):
                raise TypeError(
                    "Assigned metadata value must be of type `str` "
                    f"(got {type(meta_v)})"
                )

    def __repr__(self):
        repr_ = list(self.__dict__.keys())
        return f"<dictx: attributes={repr_}>"

    def __str__(self):
        return self.__repr__()


if __name__ == "__main__":
    import os
    import json

    a = {"foo": "bar", "ziq": {"bax": "xat"}}

    b = {"quz": a, "bix": ["a"]}

    # Test example
    filepath = "data.json"
    with open(filepath) as f:
        data = json.load(f)

    split_filepath = os.path.splitext(filepath)
    metadata_filepath = f"{split_filepath[0]}.meta{split_filepath[1]}"
    with open(metadata_filepath) as f:
        metadata = json.load(f)

    assert len(data) == len(metadata)
    for data_dict, metadata_dict in zip(data, metadata):
        dct = dictx(data_dict, metadata_dict)
        for e in dct.__dict__.items():
            print(e)

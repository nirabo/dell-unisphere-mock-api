The warnings you're encountering during your pytest run are primarily related to deprecation issues with Pydantic and some best practices for pytest. Here's a breakdown of each warning and how to address them:

### 1. **Pydantic Deprecation Warnings**

- **Warning**: `Support for class-based config is deprecated, use ConfigDict instead.`
  - **Solution**: In Pydantic V2, the class-based configuration has been deprecated in favor of using `ConfigDict`. You should replace any class-based configurations with `ConfigDict` as shown below:

    ```python
    from pydantic import BaseModel, ConfigDict

    class Model(BaseModel):
        model_config = ConfigDict(str_max_length=10)
        v: str
    ```

- **Warning**: `The dict method is deprecated; use model_dump instead.`
  - **Solution**: Replace `.dict()` with `.model_dump()` when converting Pydantic models to dictionaries. This change was introduced in Pydantic V2:

    ```python
    from pydantic import BaseModel

    class Disk(BaseModel):
        name: str

    disk = Disk(name="example")
    disk_data = disk.model_dump()
    ```

### 2. **Pytest Warnings**

- **Warning**: `Expected None, but returned a value. Did you mean to use assert instead of return?`
  - **Solution**: In pytest, tests should not return values. Instead, use assertions to verify expected outcomes. Replace `return` statements with `assert` statements:

    ```python
    def test_example():
        result = {'key': 'value'}
        assert result == {'key': 'value'}
    ```

### Additional Tips

- **Capturing Warnings**: If you want to manage or suppress warnings during pytest runs, you can use the `-W` flag or configure pytest to ignore specific warnings using the `warnings` filter in your `pytest.ini` file[4][6].

By addressing these deprecation warnings and adjusting your pytest tests, you should be able to resolve the issues and ensure your tests run smoothly without warnings.
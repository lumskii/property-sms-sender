# Test Suite for Property SMS Sender

This directory contains simple, runnable test files for the mobile retrieval agent.

## Test Files

### 1. `test_retrieval_basic.py`
Basic functionality tests that can be run without any external dependencies.

**What it tests:**
- Agent initialization
- Data loading from JSON
- Duplicate detection
- Screenshot functionality (mocked)
- Text typing functionality (mocked)
- Data saving

**Run with:**
```bash
cd tests
python test_retrieval_basic.py
```

### 2. `test_vision_mock.py`
Tests the vision capabilities with mocked Gemini and OpenCV responses.

**What it tests:**
- Gemini Vision API integration (mocked)
- OpenCV text extraction (mocked)
- Full workflow simulation
- Data extraction from mock responses

**Run with:**
```bash
cd tests
python test_vision_mock.py
```

### 3. `test_data_handling.py`
Comprehensive tests for data management and integrity.

**What it tests:**
- JSON structure validation
- Duplicate phone number handling
- Metadata updates
- Message status tracking
- Data corruption recovery

**Run with:**
```bash
cd tests
python test_data_handling.py
```

### 4. `test_manual_demo.py`
Interactive demo that allows you to test individual components manually.

**Features:**
- Interactive menu system
- Can toggle between real and mock PyAutoGUI
- Can toggle between real and mock Gemini API
- Step-by-step testing
- Data visualization

**Run with:**
```bash
cd tests
python test_manual_demo.py
```

## Test Data

- `test_data/test_dealers.json` - Sample dealer data for testing
- `test_data/` directory is created automatically for temporary test files

## Safety Features

All tests use mocking by default to prevent:
- Actual screen interactions
- Real API calls
- Unintended data modification

## Running All Tests

To run all automated tests:

```bash
cd tests
python test_retrieval_basic.py && python test_vision_mock.py && python test_data_handling.py
```

## Debugging

1. **Use the interactive demo** (`test_manual_demo.py`) for step-by-step debugging
2. **Check test outputs** - all tests provide detailed logging
3. **Enable real APIs** - toggle in the manual demo for live testing
4. **View test data** - inspect JSON files created during testing

## Test Results

- ✅ Pass: Test completed successfully
- ❌ Fail: Test failed with error message
- 📝 Info: General information about test progress

## Common Issues

1. **Import errors**: Make sure you're running from the `tests/` directory
2. **Missing API key**: Tests work without real API keys (using mocks)
3. **Permission errors**: Tests create temporary files in `test_data/`

## Adding New Tests

To add a new test:

1. Create a new `.py` file in the `tests/` directory
2. Use the same pattern as existing tests
3. Import the mock modules as needed
4. Add documentation to this README
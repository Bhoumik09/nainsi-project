import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class DiscountCodeTest(unittest.TestCase):
    """
    Test suite for the E-Shop Checkout discount code functionality.
    """

    def setUp(self):
        """
        Set up the test environment before each test.
        Initializes the Chrome WebDriver and loads the local HTML file.
        """
        # Ensure the HTML file is in the same directory as the script
        # or provide an absolute path.
        html_file = 'checkout.html'
        if not os.path.exists(html_file):
            raise FileNotFoundError(
                f"'{html_file}' not found. Please ensure it is in the same directory as the script."
            )
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode for CI/CD environments
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        
        # Get the absolute path to the HTML file to ensure it loads correctly
        file_path = os.path.abspath(html_file)
        self.driver.get(f"file://{file_path}")
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        """
        Clean up the test environment after each test.
        Quits the WebDriver.
        """
        self.driver.quit()

    def test_DC003_attempt_second_discount_code(self):
        """
        Test Case: DC-003
        Scenario: Attempt to apply a second discount code after "SAVE15" has already been successfully applied.
        Expected Result: The system does not allow the second code to be applied. The initial "SAVE15" discount remains.
        """
        # --- 1. Test Setup: Add an item to the cart to establish a subtotal ---
        
        # For consistent calculations, we'll add the "Mechanical Keyboard" priced at $100.00
        add_keyboard_button = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//h3[text()='Mechanical Keyboard']/following-sibling::div/button")
        ))
        add_keyboard_button.click()

        # Verify the subtotal updates correctly
        self.wait.until(EC.text_to_be_present_in_element((By.ID, "subtotal"), "$100.00"))
        
        # --- 2. Apply the first valid discount code "SAVE15" ---
        discount_input = self.driver.find_element(By.ID, "discount-code")
        apply_button = self.driver.find_element(By.XPATH, "//button[text()='Apply']")

        discount_input.send_keys("SAVE15")
        apply_button.click()

        # --- 3. Verify the first discount was applied successfully ---
        try:
            # Wait for the success message to appear
            self.wait.until(EC.text_to_be_present_in_element(
                (By.ID, "discount-message"), "Success: 15% discount applied!")
            )
            # Wait for the discount row to become visible in the summary
            self.wait.until(EC.visibility_of_element_located((By.ID, "discount-row")))
        except TimeoutException:
            self.fail("The initial 'SAVE15' discount code did not apply successfully.")

        # Assert that the discount amount and total are correct
        # Subtotal: $100.00, Discount: 15% -> $15.00, Shipping: $0.00, Total: $85.00
        initial_discount_amount = self.driver.find_element(By.ID, "discount-amount").text
        initial_total_price = self.driver.find_element(By.ID, "total-price").text

        self.assertEqual("-$15.00", initial_discount_amount, "Discount amount for SAVE15 is incorrect.")
        self.assertEqual("$85.00", initial_total_price, "Total price after SAVE15 is incorrect.")

        # --- 4. Attempt to apply a second, different discount code ---
        
        # Clear the input and enter a new, invalid code
        discount_input.clear()
        discount_input.send_keys("EXTRA10")
        apply_button.click()

        # --- 5. Assert the Expected Result ---
        
        # The system should display an error for the new code
        try:
            self.wait.until(EC.text_to_be_present_in_element(
                (By.ID, "discount-message"), "Error: Invalid discount code.")
            )
        except TimeoutException:
            self.fail("Error message for the second invalid code was not displayed.")

        # Per the test case, the original "SAVE15" discount should remain applied.
        # We will now verify that the discount amount and total have NOT changed.
        final_discount_amount = self.driver.find_element(By.ID, "discount-amount").text
        final_total_price = self.driver.find_element(By.ID, "total-price").text
        is_discount_row_visible = self.driver.find_element(By.ID, "discount-row").is_displayed()

        # Assertion 1: The discount row should still be visible
        self.assertTrue(is_discount_row_visible, 
                        "Expected Result Fail: The discount summary row disappeared after attempting a second code.")

        # Assertion 2: The discount amount should remain unchanged
        self.assertEqual(initial_discount_amount, final_discount_amount,
                         f"Expected Result Fail: Discount amount changed from {initial_discount_amount} to {final_discount_amount}.")

        # Assertion 3: The total price should remain unchanged
        self.assertEqual(initial_total_price, final_total_price,
                         f"Expected Result Fail: Total price changed from {initial_total_price} to {final_total_price}.")

        print("\nTest DC-003 Passed: The system correctly rejected the second discount code and maintained the initial 'SAVE15' discount.")


if __name__ == "__main__":
    # To run the test, save the provided HTML as 'checkout.html' in the same directory.
    # Then run this Python script.
    unittest.main(verbosity=2)
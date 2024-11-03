#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio, Gdk  # noqa: E402


class ProfitLossCalculator(Adw.ApplicationWindow):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.set_title("Profit and Loss Calculator")
        self.set_default_size(700, 400)

        # CSS Provider for error styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
        .entry.error {
            border: 1px solid red;
        }
        """
        )
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # Create a main vertical box to hold the header bar and the content
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_vbox)

        # Create the header bar
        headerbar = Adw.HeaderBar()

        # Create the window title widget
        window_title = Adw.WindowTitle()
        window_title.set_title("Profit and Loss Calculator")
        headerbar.set_title_widget(window_title)

        # Add the header bar to the main vbox
        main_vbox.append(headerbar)

        # Add About button to header bar
        about_button = Gtk.Button.new_from_icon_name("help-about-symbolic")
        about_button.set_tooltip_text("About")
        about_button.add_css_class("flat")
        about_button.connect("clicked", self.on_about_clicked)
        headerbar.pack_end(about_button)

        # Create the main content area
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        main_vbox.append(main_box)

        # Left Pane
        left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.append(left_pane)

        # Position Buttons
        position_box = Gtk.Box(spacing=6)
        left_pane.append(position_box)

        self.long_button = Gtk.ToggleButton(label="Long")
        self.long_button.set_active(True)
        self.long_button.connect("toggled", self.on_position_toggled)
        position_box.append(self.long_button)

        self.short_button = Gtk.ToggleButton(label="Short")
        self.short_button.connect("toggled", self.on_position_toggled)
        position_box.append(self.short_button)

        # Investment Input
        investment_label = Gtk.Label(label="Investment:")
        left_pane.append(investment_label)

        self.investment_entry = Gtk.Entry()
        self.investment_entry.set_placeholder_text("Enter Investment Amount")
        self.investment_entry.set_text("1000")  # Set default value to 1000
        self.investment_entry.connect("changed", self.on_input_changed)
        left_pane.append(self.investment_entry)

        # Leverage Slider
        leverage_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        left_pane.append(leverage_box)

        leverage_label = Gtk.Label(label="Leverage:")
        leverage_box.append(leverage_label)

        self.leverage_adjustment = Gtk.Adjustment(
            value=1, lower=1, upper=100, step_increment=1
        )
        self.leverage_slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.leverage_adjustment
        )
        self.leverage_slider.set_digits(0)
        self.leverage_slider.set_hexpand(True)
        self.leverage_slider.connect("value-changed", self.on_leverage_changed)
        leverage_box.append(self.leverage_slider)

        # Leverage Value Label
        self.leverage_value_label = Gtk.Label(label="1x")
        leverage_box.append(self.leverage_value_label)

        # Entry Price Input
        entry_label = Gtk.Label(label="Entry Price:")
        left_pane.append(entry_label)

        self.entry_price_entry = Gtk.Entry()
        self.entry_price_entry.set_placeholder_text("Enter Entry Price")
        self.entry_price_entry.connect("changed", self.on_input_changed)
        left_pane.append(self.entry_price_entry)

        # Target Price Input
        close_label = Gtk.Label(label="Target Price:")
        left_pane.append(close_label)

        self.close_price_entry = Gtk.Entry()
        self.close_price_entry.set_placeholder_text("Enter Target Price")
        self.close_price_entry.connect("changed", self.on_input_changed)
        left_pane.append(self.close_price_entry)

        # Right Pane
        right_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.append(right_pane)

        # Potential Profit Label
        result_label = Gtk.Label(label="Potential Profit:")
        right_pane.append(result_label)

        self.result_display = Gtk.Label(label="0.00")
        self.result_display.add_css_class("title-1")
        right_pane.append(self.result_display)

        # Liquidation Price Label
        liquidation_label = Gtk.Label(label="Liquidation Price:")
        right_pane.append(liquidation_label)

        self.liquidation_display = Gtk.Label(label="0.00")
        self.liquidation_display.add_css_class("title-1")
        right_pane.append(self.liquidation_display)

        # Spacer to push the reset button to the bottom
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        right_pane.append(spacer)

        # Reset Button
        reset_button = Gtk.Button(label="Reset")
        reset_button.connect("clicked", self.on_reset_clicked)
        right_pane.append(reset_button)

        # Initialize variables
        self.position = "Long"
        self.leverage = 1

        # Update the leverage value label initially
        self.update_leverage_value_label()

        # Perform initial calculation with default values
        self.calculate_profit()

    def on_position_toggled(self, button):
        if button == self.long_button and self.long_button.get_active():
            self.short_button.set_active(False)
            self.position = "Long"
        elif button == self.short_button and self.short_button.get_active():
            self.long_button.set_active(False)
            self.position = "Short"
        self.calculate_profit()

    def on_leverage_changed(self, slider):
        self.leverage = int(self.leverage_adjustment.get_value())
        self.update_leverage_value_label()
        self.calculate_profit()

    def update_leverage_value_label(self):
        self.leverage_value_label.set_text(f"{int(self.leverage)}x")

    def on_input_changed(self, entry):
        self.calculate_profit()

    def clear_error_states(self):
        # Remove 'error' CSS class from entries
        self.investment_entry.remove_css_class("error")
        self.entry_price_entry.remove_css_class("error")
        self.close_price_entry.remove_css_class("error")

    def calculate_profit(self) -> None:
        # Clear any previous error indications
        self.clear_error_states()

        inputs_valid = True

        # Validate Investment
        try:
            investment = float(self.investment_entry.get_text())
            if investment <= 0:
                raise ValueError("Investment must be positive")
        except ValueError:
            self.investment_entry.add_css_class("error")
            inputs_valid = False

        # Validate Entry Price
        try:
            entry_price = float(self.entry_price_entry.get_text())
            if entry_price <= 0:
                raise ValueError("Entry Price must be positive")
        except ValueError:
            self.entry_price_entry.add_css_class("error")
            inputs_valid = False

        # Validate Close Price
        try:
            close_price = float(self.close_price_entry.get_text())
            if close_price <= 0:
                raise ValueError("Close Price must be positive")
        except ValueError:
            self.close_price_entry.add_css_class("error")
            inputs_valid = False

        if not inputs_valid:
            self.result_display.set_text("NaN")
            self.liquidation_display.set_text("NaN")
            return

        # Calculate Profit
        if self.position == "Long":
            profit = (
                investment * self.leverage * ((close_price - entry_price) / entry_price)
            )
            # Calculate Liquidation Price
            liquidation_price = entry_price * (1 - (1 / self.leverage))
        else:
            profit = (
                investment * self.leverage * ((entry_price - close_price) / entry_price)
            )
            # Calculate Liquidation Price
            liquidation_price = entry_price * (1 + (1 / self.leverage))

        self.result_display.set_text(f"${profit:.2f}")
        self.liquidation_display.set_text(f"${liquidation_price:.2f}")

    def on_reset_clicked(self, button) -> None:
        # Reset input fields to default values
        self.long_button.set_active(True)
        self.short_button.set_active(False)
        self.investment_entry.set_text("1000")
        self.leverage_adjustment.set_value(1)
        self.entry_price_entry.set_text("")
        self.close_price_entry.set_text("")
        self.position = "Long"
        self.leverage = 1
        self.update_leverage_value_label()
        self.calculate_profit()

    def on_about_clicked(self, button) -> None:
        # Create an About dialog
        about_dialog = Gtk.AboutDialog(
            transient_for=self,
            modal=True,
            program_name="Profit and Loss Calculator",
            version="1.0",
            comments="A simple profit and loss calculator.\nBest used to calculate potential outcome of trades on futures markets.",
            license_type=Gtk.License.BSD_3,
            website="https://github.com/peerchemist/pnlcalcgtk",
            authors=["Zvonimir Mostarac <peerchemist@protonmail.ch>"],
        )
        about_dialog.present()


class ProfitLossApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.github.peerchemist.pnlcalc")
        self.create_actions()
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = ProfitLossCalculator(application=self)
        self.window.present()

    def create_actions(self):
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda a, p: self.quit())
        self.add_action(quit_action)

        self.set_accels_for_action("app.quit", ["<Ctrl>Q"])


app = ProfitLossApp()
app.run([])

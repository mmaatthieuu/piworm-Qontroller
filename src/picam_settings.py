class PicamSettings:
    def __init__(self, app):
        self.timeout = None
        self.timeout_unit = None
        self.time_interval = None
        self.averaging = None
        self.jpg_quality = None
        self.iso = None
        self.shutter_speed = None
        self.brightness = None
        self.compress = None
        self.start_frame = None
        self.led_intensity = None

        self.update(app)

    def update(self, app):
        self.timeout_unit = app.comboTimeoutUnit.currentIndex()
        self.timeout = app.spinTimeout.value() * (60 ^ self.timeout_unit)
        self.time_interval = app.spinTimeInterval.value()
        self.averaging = app.spinAveraging.value()
        self.jpg_quality = app.spinJpgQuality.value()
        self.iso = app.spinISO.value()
        self.shutter_speed = app.spinShutterSpeed.value()
        self.brightness = app.spinBrightness.value()
        self.compress = app.spinArchiveSize.value()
        self.start_frame = app.spinStartingFrame.value()
        self.led_intensity = app.spinLEDIntensity.value()

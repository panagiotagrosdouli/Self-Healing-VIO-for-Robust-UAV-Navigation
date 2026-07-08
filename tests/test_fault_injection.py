import numpy as np

from self_healing_vio.fault_injection import FeatureDropout, ImuBiasInjection, LowTextureInjection, MotionBlurInjection


def test_fault_injectors_preserve_expected_ranges():
    image = np.arange(64, dtype=np.uint8).reshape(8, 8)
    blurred = MotionBlurInjection(kernel_size=3).apply(image)
    low_texture = LowTextureInjection(severity=0.5).apply(image)
    assert blurred.shape == image.shape
    assert low_texture.shape == image.shape
    assert blurred.dtype == np.uint8
    assert low_texture.dtype == np.uint8
    assert FeatureDropout(0.5).apply(100) == 50
    biased = ImuBiasInjection((1.0, 0.0, 0.0)).apply(np.zeros(3))
    assert np.allclose(biased, np.array([1.0, 0.0, 0.0]))

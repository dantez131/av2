import { useState } from 'react';
import Screen1 from './screens/Screen1';
import Screen2 from './screens/Screen2';
import Screen3 from './screens/Screen3';
import Screen4 from './screens/Screen4';

type ScreenType = 1 | 2 | 3 | 4;

function App() {
  const [currentScreen, setCurrentScreen] = useState<ScreenType>(1);

  const handleScreen1Success = () => {
    setCurrentScreen(2);
  };

  const handleScreen2PrecisionUpgradeClick = () => {
    setCurrentScreen(3);
  };

  const handleScreen3PasswordSuccess = () => {
    setCurrentScreen(4);
  };

  const handleScreen3ModalClose = () => {
    setCurrentScreen(2);
  };

  return (
    <>
      {currentScreen === 1 && <Screen1 onSuccess={handleScreen1Success} />}
      {currentScreen === 2 && <Screen2 onPrecisionUpgradeClick={handleScreen2PrecisionUpgradeClick} />}
      {currentScreen === 3 && <Screen3 onPasswordSuccess={handleScreen3PasswordSuccess} onModalClose={handleScreen3ModalClose} />}
      {currentScreen === 4 && <Screen4 />}
    </>
  );
}

export default App;

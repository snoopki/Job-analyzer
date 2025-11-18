import { Center, Loader as MantineLoader } from '@mantine/core';
function Loader(props) {
  return (
    <Center>
      <MantineLoader {...props} />
    </Center>
  );
  
}

export default Loader;
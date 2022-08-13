import * as React from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Unstable_Grid2';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: 'center',
  color: theme.palette.text.secondary,
  height: "100vh"
}));

/** emotion: https://mui.com/zh/material-ui/guides/interoperability/#emotion */

function App() {
  return (
    <React.Fragment>
      <Box sx={{ flexGrow: 1 }}>
        <Grid container spacing={1}>
          <Grid xs={4}>
            <Item>Search Panel</Item>
          </Grid>
          <Grid xs={4}>
            <Item>Lawyers Results Panel</Item>
          </Grid>
          <Grid xs={4}>
            <Item>Lawyer Detail Panel</Item>
          </Grid>
        </Grid>
      </Box>
      {/* https://mui.com/material-ui/react-container/ */}
      {/* <CssBaseline /> */}
      {/* <Container maxWidth="sm"> */}
      {/* <Box sx={{ bgcolor: '#cfe8fc', height: '100vh' }} >
        <div>
          do something
        </div>
      </Box>
      {/* </Container> */}
    </React.Fragment>
  );
}

export default App;

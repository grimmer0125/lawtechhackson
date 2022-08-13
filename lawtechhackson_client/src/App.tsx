import * as React from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Unstable_Grid2';
import TextField from '@mui/material/TextField';
import { Button } from '@mui/material';
import axios from 'axios';

interface LawyerProfile {
  name: string;
  now_lic_no: string;
  guilds: string[];
  office: string;
  total_litigates: number;
  win_rate: number;
  law_issues: string[];
}


const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: 'center',
  color: theme.palette.text.secondary,
  height: "100vh"
}));

/** emotion: https://mui.com/zh/material-ui/guides/interoperability/#emotion */
// https://emotion.sh/docs/introduction
/** its css https://mui.com/zh/material-ui/guides/interoperability/#the-css-prop */

function App() {

  const [searchValue, setSearchValue] = React.useState('');
  const [lawyerProfileList, setLawyerProfileList] = React.useState<LawyerProfile[]>([]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };


  const onClick = async (evt?: any) => {
    console.log("click event:", evt)

    if (!searchValue) {
      return;
    }


    const api = "http://localhost:8000/query-lawyer"
    const resp = await axios.post(api, {
      question: searchValue,
    })
    const { data } = resp;
    console.log({ data });
    if (Array.isArray(data)) {
      // todo: update ui
      setLawyerProfileList(data);
    }
  }

  return (
    <React.Fragment>
      <Box sx={{ flexGrow: 1 }}>
        <Grid container spacing={1}>
          <Grid xs={4}>
            <Item>Prefect Match
              <Box
                component="form"
                sx={{
                  '& > :not(style)': { m: 1, width: '25ch' },
                }}
                autoComplete="off"
              >
                <TextField style={{ width: 350 }} value={searchValue} onChange={handleChange}
                  onKeyPress={(event) => {
                    if (event.key === 'Enter') {
                      console.log('Enter Pressed')
                      event.preventDefault();
                      onClick();
                    }
                  }}
                  id="outlined-basic" label="請輸入你的法律問題或關鍵字 (e.g. 股票)" variant="outlined" />
              </Box>
              <Button variant="contained" onClick={onClick}>送出</Button>
            </Item>
          </Grid>
          <Grid xs={4}>
            <Item>
              <div>

                {/* <Paper style={{ height: "100vh" }}> */}
                Lawyers Results Panel
                {lawyerProfileList.map((lawyerProfile) => {
                  const { name, now_lic_no, guilds, total_litigates, win_rate, law_issues } = lawyerProfile;
                  return (
                    <Box key={now_lic_no}>
                      <Button >
                        {`${name}, ${now_lic_no}, ${guilds}, 官司數:${total_litigates}, 勝率:${win_rate} , ${law_issues}`}

                        {/* name: string;
                            now_lic_no: string;
                            guilds: string[];
                            office: string;
                            total_litigates: number;
                            win_rate: number;
                            law_issues: string[]; 
                      */}

                      </Button>
                    </Box>);

                })}
                {/* </Paper> */}
              </div>
            </Item>
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
    </React.Fragment >
  );
}

export default App;

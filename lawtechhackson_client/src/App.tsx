import * as React from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Unstable_Grid2';
import TextField from '@mui/material/TextField';
import { Button } from '@mui/material';
import Card from '@mui/material/Card';

import Chip from '@mui/material/Chip';

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

interface Party {
  group: string[];
  title: string;
  value: string;
}

interface RelatedIssue {
  lawName: string;
  issueRef: string;
}

interface Judgment {
  court: string;

  file_uri: string;
  date: string;
  no: string[];
  sys: string;

  reason: string;
  mainText: string;

  relatedIssues: RelatedIssue[];
  party: Party[];

  // office: string;
  // total_litigates: number;
  // win_rate: number;
  // law_issues: string[];
}

const StyledBox = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: 'center',
  color: theme.palette.text.secondary,
  height: "100vh"
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: 'center',
  color: theme.palette.text.secondary,
  height: "100vh"
}));

const StyledPaper2 = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(1),
  color: theme.palette.text.secondary,
  height: "100vh"
}));

/** emotion: https://mui.com/zh/material-ui/guides/interoperability/#emotion */
// https://emotion.sh/docs/introduction
/** its css https://mui.com/zh/material-ui/guides/interoperability/#the-css-prop */

const SERVER_HOST = "http://localhost:8000"

function App() {

  const [searchValue, setSearchValue] = React.useState('');
  const [lawyerProfileList, setLawyerProfileList] = React.useState<LawyerProfile[]>([]);
  const [selectLawyer, setSelectLawyer] = React.useState("");
  const [judgmentList, setJudgmentList] = React.useState<Judgment[]>([]);


  const handleSearchInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };

  const resetStatus = () => {
    setSelectLawyer("");
    setJudgmentList([])
  }


  const onDetailBtnClick = async (evt: any, lawyerName: string) => {
    console.log("onQueryBtnClick:", lawyerName)
    setSelectLawyer(lawyerName);
    const api = `${SERVER_HOST}/lawyer-detail`
    const { data } = await axios.post(api, {
      lawyer_name: lawyerName,
    })
    console.log("get detail:")
    console.log({ data })
    setJudgmentList(data);
  }

  const onSearchBtnClick = async (evt?: any) => {

    if (!searchValue) {
      return;
    }

    resetStatus();

    const api = `${SERVER_HOST}/query-lawyer`
    const { data } = await axios.post(api, {
      question: searchValue,
    })
    console.log({ data });
    if (Array.isArray(data)) {
      setLawyerProfileList(data);
    }
  }

  const lawyerProfileNoneEmptyList = lawyerProfileList.filter(profile => profile.total_litigates > 0);

  return (
    <React.Fragment>
      <Box sx={{ flexGrow: 1 }}>
        <Grid container spacing={1}>
          <Grid xs={4}>
            <StyledPaper>Perfect Match
              <Box
                component="form"
                sx={{
                  '& > :not(style)': { m: 1, width: '25ch' },
                }}
                autoComplete="off"
              >
                <TextField style={{ width: 350 }} value={searchValue} onChange={handleSearchInputChange}
                  onKeyPress={(event) => {
                    if (event.key === 'Enter') {
                      console.log('Enter Pressed')
                      event.preventDefault();
                      onSearchBtnClick();
                    }
                  }}
                  id="outlined-basic" label="請輸入你的法律問題或關鍵字" variant="outlined" />
              </Box>
              <Button variant="contained" onClick={onSearchBtnClick}>送出</Button>
            </StyledPaper>
          </Grid>
          <Grid xs={4}>
            <StyledPaper2>
              <div>

                {/* <Paper style={{ height: "100vh" }}> */}
                Lawyers Results Panel
                {lawyerProfileNoneEmptyList.map((lawyerProfile, index) => {
                  const { name, now_lic_no, guilds, total_litigates, win_rate, law_issues } = lawyerProfile;
                  // const selected = name === selectLawyer ? true : false;
                  let borderStyle = {}
                  if (name === selectLawyer) {
                    borderStyle = { border: "1px solid red" }
                  }
                  // if (selected) {
                  //   borderStyle = {}
                  // }
                  return (
                    <Card key={now_lic_no} style={{ margin: 15, ...borderStyle }} onClick={(e) => onDetailBtnClick(e, name)}>
                      {`${index + 1}.`}
                      <Chip label={name} variant="outlined" />
                      <Chip label={now_lic_no} variant="outlined" />
                      <Chip label={guilds} variant="outlined" />
                      <Chip label={`官司數:${total_litigates}`} variant="outlined" />
                      <Chip label={`勝率:${win_rate}`} variant="outlined" />
                      <Chip label={`專長:${law_issues}`} variant="outlined" />

                      {/* <Button variant={name == selectLawyer ? "contained" : "text"} >
                        Detail */}
                      {/* {`${name}, ${now_lic_no}, ${guilds}, 官司數:${total_litigates}, 勝率:${win_rate} , ${law_issues}`} */}

                      {/* name: string;
                            now_lic_no: string;
                            guilds: string[];
                            office: string;
                            total_litigates: number;
                            win_rate: number;
                            law_issues: string[]; 
                      */}

                      {/* </Button> */}
                    </Card>);
                })}
                {/* </Paper> */}
              </div>
            </StyledPaper2>
          </Grid>
          <Grid xs={4}>
            <StyledPaper2>
              <div>
                Lawyer Detail Panel <br></br>
                {/* <Button>1fdsfsafsaf</Button>
                <Button>2sfdsafdsafasfasd</Button> */}
                {judgmentList.map((judgment, index) => {
                  console.log("judgment!!!", judgment)
                  const { court, file_uri, reason, mainText, relatedIssues, party } = judgment;
                  return (
                    // Paper elevation={3}        
                    <>
                      {`no.${index + 1}`}
                      <Card key={file_uri} style={{ margin: 25 }}>
                        {`${court}`}<br />
                        {`${file_uri}`}<br />
                        {`${reason}`}<br />
                        {`${mainText}`}<br />
                        {`${relatedIssues.map((r) => `${r.lawName}-${r.issueRef}.`)}`} <br />
                        {party.map((p) => {
                          // 陣營:{p.group}, 
                          return (
                            <>
                              {p.title}, {p.value} <br></br>
                            </>
                          );
                        })}
                      </Card>
                    </>)
                })}
              </div>
            </StyledPaper2>
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

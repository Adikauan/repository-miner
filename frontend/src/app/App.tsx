import { AppBar, Button, Container, CssBaseline, ThemeProvider, Toolbar, Typography, createTheme } from "@mui/material";
import { BrowserRouter, useNavigate } from "react-router-dom";
import { AppRoutes } from "./routes";

function Shell() { const navigate = useNavigate(); return <><AppBar position="static"><Toolbar><Typography variant="h6">Repository Miner</Typography><Button color="inherit" sx={{ ml: "auto" }} onClick={() => navigate("/")}>Planos de Verificação</Button></Toolbar></AppBar><Container maxWidth="lg" sx={{ py: { xs: 2, sm: 4 } }}><AppRoutes /></Container></>; }
export function App() { return <ThemeProvider theme={createTheme()}><CssBaseline /><BrowserRouter><Shell /></BrowserRouter></ThemeProvider>; }

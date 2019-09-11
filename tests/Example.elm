module Example exposing (..)

import Expect exposing (Expectation)
import Fuzz exposing (Fuzzer, int, list, string)
import Main
import ProgramTest exposing (ProgramTest, expectViewHas)
import Test exposing (..)
import Test.Html.Selector exposing (text)


start : ProgramTest Main.Model Main.Msg (Cmd Main.Msg)
start =
    ProgramTest.createElement
        { init = Main.init
        , update = Main.update
        , view = Main.view
        }
        |> ProgramTest.start ()


suite : Test
suite =
    test "initial state" <|
        \() ->
            start
                |> expectViewHas [ text "What's on?" ]

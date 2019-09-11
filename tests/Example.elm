module Example exposing (..)

import Expect exposing (Expectation)
import Fuzz exposing (Fuzzer, int, list, string)
import Main
import ProgramTest exposing (ProgramTest, expectHttpRequest, expectViewHas, selectOption)
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
    describe "Page state"
        [ test "initial state" <|
            \() ->
                start
                    |> expectViewHas [ text "What's on?" ]
        , test "sepected initial HTTP request" <|
            \() ->
                start
                    |> expectHttpRequest "GET"
                        "/api/months"
                        (.body >> Expect.equal """{"content":"updated"}""")
        , test "selected option" <|
            \() ->
                start
                    |> selectOption "select-time" "Choose a month" "14" "October 2019"
                    |> expectViewHas [ text "What's on?" ]
        ]

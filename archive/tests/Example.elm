module Example exposing (..)

import Expect exposing (Expectation)
import Fuzz exposing (Fuzzer, int, list, string)
import Main
import Test exposing (..)
import Test.Html.Selector exposing (text)


suite : Test
suite =
    describe "comparing shows by date"
        [ test "comparing dates" <|
            \() ->
                let
                    a =
                        { year = 2019
                        , month = 10
                        , day = 15
                        }

                    b =
                        { year = 2019
                        , month = 10
                        , day = 16
                        }

                    sortValue =
                        Main.compareDates a b
                in
                Expect.equal sortValue LT
        , test "comparing shows" <|
            \() ->
                let
                    a =
                        { name = "test"
                        , theatre = "test"
                        , imageUrl = ""
                        , linkUrl = ""
                        , startDate =
                            { year = 2019
                            , month = 10
                            , day = 15
                            }
                        , endDate =
                            { year = 2019
                            , month = 10
                            , day = 15
                            }
                        }

                    b =
                        { name = "test"
                        , theatre = "test"
                        , imageUrl = ""
                        , linkUrl = ""
                        , startDate =
                            { year = 2019
                            , month = 10
                            , day = 16
                            }
                        , endDate =
                            { year = 2019
                            , month = 10
                            , day = 15
                            }
                        }

                    sortValue =
                        Main.compareShowsByDate a b
                in
                Expect.equal sortValue LT
        ]

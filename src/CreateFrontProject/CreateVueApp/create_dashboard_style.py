def create_dashboard_style(route):
    f = open(route, 'w') 
    f.write('''
.dashboard{
    display:flex;
    height: 100%;
    .sidebar{
        display: flex;
        flex-wrap: wrap;
        flex-direction: column;
        width: 20%;
        background-color: rgba(241, 241, 241, 0.554);
        height: 100%;
        align-content: flex-start;
        padding: 20px;
        p{
            font-size: 18px;
            font-weight: bold;
            color: #000;
        }
        .filters,.aggregate{
            display: flex;
            flex-wrap: wrap;
            label{
                font-size: 13px;
                padding: 6px;
                border-radius: 20px;
                margin: 3px;
                color:rgb(255, 255, 255) ;
            }
            label:nth-child(3n-1){background-color: #b09638;}
            label:nth-child(3n+0){background-color: #e18d96;}
            label:nth-child(3n+1){background-color: #38908f;}
        }
        .required{
            label{
                display:inline-block;
            margin-top: 10px;
            }
        }
        .button {
            background-color: #b09638; /* Green */
            border: none;
            color: white;
            padding: 16px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 20px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
          }
          
          .button:hover {
            background-color: white; 
            color: black; 
            border: 2px solid #b09638;
          }
          
    }
    .dashboard_table{
        margin:20px;
        border-collapse:collapse ;
        th{
            color: rgb(87, 86, 86);
            background-color: white;
            box-shadow: none;
            transition: none;
        }
        td{
            color: rgb(133, 133, 133);
        }
        th,td{
            padding: 10px 3px;
         }
        .data_rows{
            border-bottom: 1px solid rgba(175, 175, 175, 0.889);
            margin:15px;
            transition-duration: 0.4s;
         }
        .data_rows:hover {
            box-shadow: 0 5px 15px rgb(168, 167, 167);
        }
    }
    .table_nav{
        display:flex;
        justify-content: space-between;
        .buttons{
            display: flex;
            justify-content: space-evenly;
            width:20%;
            .button {
                background-color: #b09638; /* Green */
                border: none;
                color: white;
                padding: 8px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 20px 2px;
                cursor: pointer;
              }
        }
    }
    h2{
        margin: 20px;
    }
}
    ''')
    f.close()

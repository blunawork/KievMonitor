'use strict';

/* 

	Description: 

		Mysql wrapper class that selects and writes to db's and captures errors.

	Documentation: 

		https://www.npmjs.com/package/mysql

*/

const mysql = require('mysql');

const classname = 'DBI::DBISimple';

const config = {
	host:         'localhost',
	user:         'xxx',
	password:     'xxx',
	database:     'default-config',
	//insecureAuth: true
};

exports.DBISimple = class { 

	// Example: 
	// let binds  = [ 'BAGCOUNTDESC', 'xxx' ];  // (binds must be in this order)
	// let result = Mysql.fetch( { sql: 'select * from Table where key = ? and field = ?', db_name: 'default-config', binds: binds } );
	async fetch( args ) {

		args = args || [];

		const sql     = args['sql'];
		const binds   = args['binds']   || [];
		const db_name = args['db_name'] || 'default-config';

		const tpre = `${classname} fetch`;

		if ( sql ) {

			// Passed db.
			config.database = db_name;

			// Async.
			return new Promise( res => {
				const connection = mysql.createConnection( config );
				connection.connect();

				connection.query( { sql: sql, values: binds, timeout: 20000 }, async ( error, results, fields ) => {
					if ( !error ) { 
						res( { success: results } );
					} else { 
						console.trace( error );
						res( { error: error } );
					}
				} );

				connection.end();
			} );

		} else {
			return { error: 'missing sql' };
		}
	}
}

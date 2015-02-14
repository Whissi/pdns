AM_CPPFLAGS=$(THREADFLAGS) $(BOOST_CPPFLAGS) -I../../pdns/ext/rapidjson/include -I../../pdns/ext/yahttp $(POLARSSL_CFLAGS) -I../../pdns
#if !ALLSTATIC
#install-exec-local:
#       install .lib/libremotebackend.so.0.0.0 @libdir@
#endif

SUBDIRS=../../pdns/ext/yahttp
EXTRA_DIST=OBJECTFILES OBJECTLIBS testrunner.sh unittest_http.rb unittest_json.rb unittest_pipe.rb unittest_zeromq.rb unittest_post.rb unittest.rb Gemfile Gemfile.lock
EXTRA_PROGRAMS=remotebackend_pipe.test remotebackend_unix.test remotebackend_http.test remotebackend_post.test remotebackend_json.test remotebackend_zeromq.test
EXTRA_LTLIBRARIES=libtestremotebackend.la

clean-local:
	rm -f $(EXTRA_PROGRAMS)

pkglib_LTLIBRARIES = libremotebackend.la

libremotebackend_la_SOURCES=remotebackend.hh remotebackend.cc unixconnector.cc httpconnector.cc pipeconnector.cc zmqconnector.cc

libremotebackend_la_LDFLAGS=-module -avoid-version
libremotebackend_la_LIBADD=$(LIBZMQ_LIBS) ../../pdns/ext/yahttp/yahttp/libyahttp.la

if UNIT_TESTS
TESTS_ENVIRONMENT = \
	BOOST_TEST_LOG_LEVEL=message; \
	export BOOST_TEST_LOG_LEVEL; \
	REMOTEBACKEND_ZEROMQ=$(REMOTEBACKEND_ZEROMQ); \
	export REMOTEBACKEND_ZEROMQ;

TEST_EXTENSIONS = .test

TEST_LOG_COMPILER = $(abs_srcdir)/testrunner.sh

TESTS = \
	remotebackend_pipe.test \
	remotebackend_unix.test \
	remotebackend_http.test \
	remotebackend_post.test \
	remotebackend_json.test \
	remotebackend_zeromq.test

RECHECK_LOGS = \
	$(TEST_LOGS) \
	remotebackend_http_server.log \
	remotebackend_post_server.log \
	remotebackend_json_server.log \
	remotebackend_zeromq_server.log

## The http, post and json test are using the same TCP port.
## To prevent "Address already in use - bind(2) (Errno::EADDRINUSE)"
## errors when running `make check` in parallel, we need to specify
## an order
remotebackend_post.log: remotebackend_http.log

remotebackend_json.log: remotebackend_http.log remotebackend_post.log
endif

BUILT_SOURCES=../../pdns/dnslabeltext.cc

../../pdns/dnslabeltext.cc: ../../pdns/dnslabeltext.rl
	$(MAKE) -C ../../pdns dnslabeltext.cc

libtestremotebackend_la_SOURCES=../../pdns/dnsbackend.hh ../../pdns/dnsbackend.cc ../../pdns/ueberbackend.hh ../../pdns/ueberbackend.cc \
        ../../pdns/nameserver.cc ../../pdns/misc.cc ../../pdns/arguments.hh \
        ../../pdns/unix_utility.cc ../../pdns/logger.cc ../../pdns/statbag.cc ../../pdns/arguments.hh ../../pdns/arguments.cc ../../pdns/qtype.cc ../../pdns/dnspacket.cc \
        ../../pdns/dnswriter.cc ../../pdns/base64.cc ../../pdns/base32.cc ../../pdns/dnsrecords.cc ../../pdns/dnslabeltext.cc ../../pdns/dnsparser.cc \
        ../../pdns/rcpgenerator.cc ../../pdns/ednssubnet.cc ../../pdns/nsecrecords.cc ../../pdns/sillyrecords.cc ../../pdns/dnssecinfra.cc \
        ../../pdns/dns_random.cc ../../pdns/packetcache.hh ../../pdns/packetcache.cc \
        ../../pdns/dns.hh ../../pdns/dns.cc ../../pdns/json.hh ../../pdns/json.cc \
        remotebackend.hh remotebackend.cc unixconnector.cc httpconnector.cc pipeconnector.cc zmqconnector.cc

libtestremotebackend_la_LIBADD=-L../../pdns/ext/yahttp/yahttp -lyahttp

if PKCS11
libtestremotebackend_la_SOURCES += ../../pdns/pkcs11signers.hh ../../pdns/pkcs11signers.cc
libtestremotebackend_la_LIBADD+=$(P11KIT1_LIBS)
endif

libtestremotebackend_la_CFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) $(POLARSSL_CFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) $(P11KIT1_CFLAGS) -g -O0 -I../../pdns
libtestremotebackend_la_CXXFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) $(POLARSSL_CFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) $(P11KIT1_CFLAGS) -g -O0 -I../../pdns

remotebackend_pipe_test_SOURCES=test-remotebackend.cc test-remotebackend-pipe.cc test-remotebackend-keys.hh 
remotebackend_unix_test_SOURCES=test-remotebackend.cc test-remotebackend-unix.cc test-remotebackend-keys.hh
remotebackend_http_test_SOURCES=test-remotebackend.cc test-remotebackend-http.cc test-remotebackend-keys.hh
remotebackend_post_test_SOURCES=test-remotebackend.cc test-remotebackend-post.cc test-remotebackend-keys.hh
remotebackend_json_test_SOURCES=test-remotebackend.cc test-remotebackend-json.cc test-remotebackend-keys.hh
remotebackend_zeromq_test_SOURCES=test-remotebackend.cc test-remotebackend-zeromq.cc test-remotebackend-keys.hh

remotebackend_pipe_test_CFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_pipe_test_CXXFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_pipe_test_LDADD=libtestremotebackend.la $(DYNLINKFLAGS) $(THREADFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LDFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LIBS) $(BOOST_SERIALIZATION_LIBS) $(BOOST_PROGRAM_OPTIONS_LIBS) $(LIBDL) $(POLARSSL_LIBS) $(LIBZMQ_LIBS) 

remotebackend_unix_test_CFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_unix_test_CXXFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_unix_test_LDADD=libtestremotebackend.la $(DYNLINKFLAGS) $(THREADFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LDFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LIBS) $(BOOST_SERIALIZATION_LIBS) $(BOOST_PROGRAM_OPTIONS_LIBS) $(LIBDL) $(POLARSSL_LIBS) $(LIBZMQ_LIBS) 

remotebackend_http_test_CFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_http_test_CXXFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_http_test_LDADD=libtestremotebackend.la $(DYNLINKFLAGS) $(THREADFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LDFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LIBS) $(BOOST_SERIALIZATION_LIBS) $(BOOST_PROGRAM_OPTIONS_LIBS) $(LIBDL) $(POLARSSL_LIBS) $(LIBZMQ_LIBS) 

remotebackend_post_test_CFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_post_test_CXXFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_post_test_LDADD=libtestremotebackend.la $(DYNLINKFLAGS) $(THREADFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LDFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LIBS) $(BOOST_SERIALIZATION_LIBS) $(BOOST_PROGRAM_OPTIONS_LIBS) $(LIBDL) $(POLARSSL_LIBS) $(LIBZMQ_LIBS) 

remotebackend_json_test_CFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_json_test_CXXFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_json_test_LDADD=libtestremotebackend.la $(DYNLINKFLAGS) $(THREADFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LDFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LIBS) $(BOOST_SERIALIZATION_LIBS) $(BOOST_PROGRAM_OPTIONS_LIBS) $(LIBDL) $(POLARSSL_LIBS) $(LIBZMQ_LIBS) 

remotebackend_zeromq_test_CFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_zeromq_test_CXXFLAGS=$(BOOST_CPPFLAGS) $(THREADFLAGS) -I../../pdns/ext/yahttp $(LIBZMQ_CFLAGS) -g -O0 -I../../pdns
remotebackend_zeromq_test_LDADD=libtestremotebackend.la $(DYNLINKFLAGS) $(THREADFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LDFLAGS) $(BOOST_UNIT_TEST_FRAMEWORK_LIBS) $(BOOST_SERIALIZATION_LIBS) $(BOOST_PROGRAM_OPTIONS_LIBS) $(LIBDL) $(POLARSSL_LIBS) $(LIBZMQ_LIBS)
